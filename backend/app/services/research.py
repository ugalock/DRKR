# backend/app/services/research.py
import os
import json
import re
import uuid
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

import httpx
from fastapi import HTTPException

from app.config import settings
from app.models import ResearchJob, ResearchService as ResearchServiceDB, ResearchServiceModel
from app.models import AiModel as AiModelDB
from app.schemas.research_job import ResearchJob as ResearchJobSchema
from app.schemas.research_job_create_request import ResearchJobCreateRequest

class ResearchService:
    def __init__(self):
        # No database or cache initialization here
        pass

    async def _get_service_config(self, db: AsyncSession, service: str) -> Dict:
        """Get the configuration for a research service"""
        # Query the service and model info from the database
        stmt = (
            select(ResearchServiceDB)
            .options(
                joinedload(ResearchServiceDB.models).joinedload(AiModelDB.service_models)
            )
            .where(ResearchServiceDB.service_key == service)
        )
        db_service = await db.execute(stmt).unique().scalar_one_or_none()
        
        if not db_service:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported research service: {service}"
            )

        repl_regex = re.compile(r"\{\{(.*?)\}\}")
        # Build configuration dictionary
        service_config = {
            "url": repl_regex.sub(lambda match: getattr(settings, match.group(1), match.group(0)), db_service.url),
            "default_model": None,
            "default_params": {}
        }

        # Find the default model
        default_model = None
        if db_service.default_model_id:
            default_model = next(
                (model for model in db_service.models 
                 if model.id == db_service.default_model_id),
                None
            )
        
        if not default_model and db_service.models:
            # If no explicit default, try to find one marked as default in the linking table
            default_model = next(
                (model for model in db_service.models 
                 if any(sm.is_default for sm in model.service_models 
                       if sm.service_id == db_service.id)),
                db_service.models[0]  # Fallback to first model if no default specified
            )

        if default_model:
            service_config["default_model"] = default_model.model_key
            service_config["default_params"] = default_model.default_params

        return service_config

    async def _validate_service(self, db: AsyncSession, service: str) -> None:
        """Validate that the requested service exists in database."""
        stmt = select(ResearchServiceDB).where(ResearchServiceDB.service_key == service)
        result = await db.execute(stmt)
        db_service = result.scalar_one_or_none()
        
        if not db_service:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported research service: {service}"
            )

    async def start_job(
        self,
        db: AsyncSession,
        service: str,
        user_id: str,
        prompt: str,
        breadth: int = 4,
        depth: int = 2,
        model: Optional[str] = None,
        model_params: Optional[Dict] = None
    ) -> Dict:
        """Start a research job via the specified service."""
        await self._validate_service(db, service)
        
        if service == "open-dr":
            # Get service configuration from database
            service_config = await self._get_service_config(db, service)
            url = service_config["url"]
            
            # Use default model if none specified
            if not model:
                model = service_config["default_model"]
            
            # Merge default and custom model params
            params = service_config["default_params"].copy()
            if model_params:
                params.update(model_params)
            if model.startswith("o") and "reasoning_effort" not in params:
                params["reasoning_effort"] = "medium"

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(url + "/research/start", json={
                    "user_id": user_id,
                    "prompt": prompt,
                    "breadth": breadth,
                    "depth": depth,
                    "model": model,
                    "model_params": params
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenDR API error: {response.text}"
                    )
                
                result = response.json()
                
                # Generate job_id if not provided by service
                job_id = result.get("job_id", str(uuid.uuid4()))
                
                # Create and save research job
                db_job = ResearchJob(
                    job_id=job_id,
                    user_id=user_id,
                    status=result.get("status", "pending_answers"),
                    service=service,
                    model_name=model,
                    model_params=params,
                    visibility="private"  # Default to private
                )
                
                await db.add(db_job)
                await db.commit()
                await db.refresh(db_job)
                
                return {
                    "job": ResearchJobSchema.model_validate(db_job),
                    "questions": result.get("questions", [])
                }

    async def answer_questions(
        self,
        db: AsyncSession,
        service: str,
        user_id: str,
        job_id: str,
        answers: List[str]
    ) -> Dict:
        """Submit answers to follow-up questions for a research job."""
        await self._validate_service(db, service)
        
        # Check if job exists first
        stmt = select(ResearchJob).where(
            ResearchJob.job_id == job_id,
            ResearchJob.user_id == user_id,
            ResearchJob.service == service
        )
        db_job = await db.execute(stmt).scalar_one_or_none()
        
        if not db_job:
            raise HTTPException(
                status_code=404,
                detail="Research job not found"
            )
        
        if service == "open-dr":
            service_config = await self._get_service_config(db, service)
            url = service_config["url"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url + "/research/answer", json={
                    "user_id": user_id,
                    "job_id": job_id,
                    "answers": answers
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenDR API error: {response.text}"
                    )
                
                result = response.json()
                
                # Update job status
                db_job.status = result["status"]
                await db.commit()
                await db.refresh(db_job)
                
                return ResearchJobSchema.model_validate(db_job)

    async def poll_status(
        self,
        db: AsyncSession,
        user_id: str,
        id: Optional[int] = None,
        job_id: Optional[str] = None,
        service: Optional[str] = None
    ) -> Dict:
        """Check the current status of a research job."""
        # Query job from database first
        if id is not None:
            stmt = select(ResearchJob).where(
                ResearchJob.id == id,
                ResearchJob.user_id == user_id
            )
        elif job_id is not None and service is not None:
            stmt = select(ResearchJob).where(
                ResearchJob.job_id == job_id,
                ResearchJob.user_id == user_id,
                ResearchJob.service == service
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either id or (job_id, service) must be provided"
            )
            
        # Fix the coroutine execution issue - first execute query, then get scalar
        result = await db.execute(stmt)
        db_job = result.scalar_one_or_none()
        
        if not db_job:
            raise HTTPException(
                status_code=404,
                detail="Research job not found"
            )
        
        # Return immediately if job is in a final state
        if db_job.status in ["complete", "failed", "cancelled"]:
            return {
                "job": ResearchJobSchema.model_validate(db_job),
                "results": None  # No need to fetch results if already complete
            }
            
        # For active jobs, poll the service
        service = db_job.service
        job_id = db_job.job_id
        await self._validate_service(db, service)
        
        if service == "open-dr":
            service_config = await self._get_service_config(db, service)
            url = service_config["url"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url + "/research/status", params={
                    "user_id": user_id,
                    "job_id": job_id
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenDR API error: {response.text}"
                    )
                
                result = response.json()
                
                # Update job status
                db_job.status = result["status"]
                if result["status"] == "complete" and "results" in result:
                    # TODO: Store research results in DeepResearch table
                    pass
                
                await db.commit()
                await db.refresh(db_job)
                
                return {
                    "job": ResearchJobSchema.model_validate(db_job),
                    "results": result.get("results")
                }

    async def cancel_job(
        self,
        db: AsyncSession,
        service: str,
        user_id: str,
        job_id: str
    ) -> Dict:
        """Cancel an in-progress research job."""
        await self._validate_service(db, service)
        
        # Check if job exists and get current status
        stmt = select(ResearchJob).where(
            ResearchJob.job_id == job_id,
            ResearchJob.user_id == user_id,
            ResearchJob.service == service
        )
        db_job = await db.execute(stmt).scalar_one_or_none()
        
        if not db_job:
            raise HTTPException(
                status_code=404,
                detail="Research job not found"
            )
            
        # Return immediately if job is already in a final state
        if db_job.status in ["complete", "failed", "cancelled"]:
            return ResearchJobSchema.model_validate(db_job)
        
        if service == "open-dr":
            service_config = await self._get_service_config(db, service)
            url = service_config["url"]
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url + "/research/cancel", params={
                    "user_id": user_id,
                    "job_id": job_id
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenDR API error: {response.text}"
                    )
                
                # Update job status to cancelled
                db_job.status = "cancelled"
                await db.commit()
                await db.refresh(db_job)
                
                return ResearchJobSchema.model_validate(db_job)

    async def list_jobs(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
        filter_params: Optional[Dict] = None
    ) -> List[Dict]:
        """List research jobs with optional filtering."""
        # Start with base query
        query = select(ResearchJob)
        
        # Apply user_id filter
        query = query.where(ResearchJob.user_id == user_id)
        
        # Apply additional filters if provided
        if filter_params:
            for key, value in filter_params.items():
                if hasattr(ResearchJob, key):
                    query = query.where(getattr(ResearchJob, key) == value)
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return [ResearchJobSchema.model_validate(job) for job in jobs]

    async def get_research_services(
        self,
        db: AsyncSession,
        service_key: Optional[str] = None
    ) -> List[ResearchServiceDB]:
        """
        Get all research services or a specific one by service_key.
        
        Args:
            db: Database session
            service_key: Optional service key to filter by
            
        Returns:
            List of research services or a single service wrapped in a list
        """
        query = select(ResearchServiceDB)
        
        # query = query.options(
        #     # Load the relationships we need
        #     selectinload(ResearchServiceDB.default_model),
        #     selectinload(ResearchServiceDB.service_models).selectinload(ResearchServiceModel.model)
        # )
        
        if service_key:
            query = query.where(ResearchServiceDB.service_key == service_key)
        
        result = await db.execute(query)
        return list(result.scalars().unique())
