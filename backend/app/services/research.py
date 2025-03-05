# backend/app/services/research.py
import os
import json
import re
import uuid
from typing import Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from cachetools import TTLCache
from urllib.parse import urlparse


import httpx
from fastapi import HTTPException
import openai

from app.config import settings
from app.models import ResearchJob, ResearchService as ResearchServiceDB, ResearchServiceModel, DeepResearch, ResearchSource
from app.schemas.research_job import ResearchJob as ResearchJobSchema
from app.schemas.research_job_create_request import ResearchJobCreateRequest
from app.tasks.research_processing import process_research_data


cache = TTLCache(maxsize=100, ttl=300)
openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def get_deep_research_title(prompt_text: str) -> str:
    prompt = f"Generate a title for the following research prompt using no more than 255 characters: {prompt_text}"
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates a title for a research report based on a prompt."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=75
    )
    return response.choices[0].message.content

class ResearchService:
    def __init__(self):
        # No database or cache initialization here
        pass

    async def _get_service_config(self, db: AsyncSession, service: str) -> Dict:
        """Get the configuration for a research service"""
        if service in cache:
            return cache[service]
        
        # Query the service and model info from the database
        stmt = (
            select(ResearchServiceDB)
            .options(
                selectinload(ResearchServiceDB.default_model),
                selectinload(ResearchServiceDB.service_models).selectinload(ResearchServiceModel.model),
                selectinload(ResearchServiceDB.models)
            )
            .where(ResearchServiceDB.service_key == service)
        )
        db_service = await db.execute(stmt)
        db_service = db_service.scalar_one_or_none()
        
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
            "default_params": {},
            "models": {}
        }

        # Find the default model
        default_model = db_service.default_model
        
        if not default_model and db_service.models:
            # If no explicit default, try to find one marked as default in the linking table
            default_model = next(
                (model for model in db_service.models 
                 if model.is_active and any(sm.is_default for sm in model.service_models 
                       if sm.service_id == db_service.id)),
                db_service.models[0]  # Fallback to first model if no default specified
            )

        if default_model:
            service_config["default_model"] = default_model.model_key
            service_config["default_params"] = default_model.default_params

        if db_service.models:
            for model in db_service.models:
                if model.is_active:
                    service_config["models"][model.model_key] = {
                        "default_params": model.default_params,
                        "max_tokens": model.max_tokens
                    }

        cache[service] = service_config
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
                default_params = service_config["default_params"]
                max_tokens = service_config["max_tokens"]
            elif model not in service_config["models"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported model: {model}"
                )
            else:
                default_params = service_config["models"][model]["default_params"]
                max_tokens = service_config["models"][model]["max_tokens"]
            
            # Merge default and custom model params
            params = default_params.copy()
            if model_params:
                params.update(model_params)
            if model.startswith("o") and "reasoning_effort" not in params:
                params["reasoning_effort"] = "medium"

            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(url + "/research/start", timeout=httpx.Timeout(10.0), json={
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
                    user_id=int(user_id),
                    status=result.get("status", "pending_answers"),
                    service=service,
                    prompt=prompt,
                    model_name=model,
                    model_params=params,
                    visibility="private"  # Default to private
                )
                
                db.add(db_job)
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
        user_id: int,
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
        db_job = await db.execute(stmt)
        db_job = db_job.scalar_one_or_none()
        
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
                    "user_id": str(user_id),
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
        user_id: int,
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
        if db_job.status in ["completed", "failed", "cancelled"]:
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
                    "user_id": str(user_id),
                    "job_id": job_id
                })
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenDR API error: {response.text}"
                    )
                
                result = response.json()
                if result["status"] == "complete":
                    db_job.status = "completed"
                else:
                    # Update job status
                    db_job.status = result["status"]
                if db_job.status == "completed" and "results" in result:
                    # Store research results in DeepResearch table
                    research_results = result.get("results", {})
                    prompt_text = research_results.get("prompt", "")
                    questions_and_answers = research_results.get("questions_and_answers", "")
                    final_report = research_results.get("report", "")
                    sources = research_results.get("sources", [])
                    
                    # Create a title from prompt (truncate if needed)
                    try:
                        title = get_deep_research_title(prompt_text)
                    except:
                        title = prompt_text[:255] if len(prompt_text) <= 255 else prompt_text[:252] + "..."
                    
                    # Create DeepResearch record
                    deep_research = DeepResearch(
                        user_id=user_id,
                        owner_user_id=user_id,  # User who created the job is the owner
                        owner_org_id=db_job.owner_org_id,  # Copy organization ownership from job
                        visibility=db_job.visibility,  # Use same visibility setting as job
                        title=title,
                        prompt_text=prompt_text,
                        questions_and_answers=questions_and_answers,
                        final_report=final_report,
                        model_name=db_job.model_name,
                        model_params=db_job.model_params,
                        source_count=len(sources)
                        # Vector embeddings will be added by the async processor
                    )
                    
                    db.add(deep_research)
                    await db.flush()  # Get ID without committing transaction
                    
                    # Add sources if available
                    for source in sources:
                        source_url = source.get("url", "")
                        source_title = source.get("title", "")
                        source_excerpt = source.get("description", "")
                        
                        # Extract domain from URL
                        domain = None
                        if source_url:
                            try:
                                parsed_url = urlparse(source_url)
                                domain = parsed_url.netloc
                            except:
                                # If URL parsing fails, leave domain as None
                                pass
                        
                        # Create source record
                        db_source = ResearchSource(
                            deep_research_id=deep_research.id,
                            source_url=source_url,
                            source_title=source_title,
                            source_excerpt=source_excerpt,
                            domain=domain,
                            source_type="website"  # Default, can be refined later
                        )
                        db.add(db_source)
                    
                    # Link the job to the research
                    db_job.deep_research_id = deep_research.id
                    await db.commit()
                    # Trigger async processing tasks
                    process_research_data.delay(deep_research.id)

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
        """Get all research services or a specific one by service_key."""
        query = select(ResearchServiceDB)
        
        # Explicitly load all relationships needed by the Pydantic schema
        query = query.options(
            selectinload(ResearchServiceDB.default_model),
            selectinload(ResearchServiceDB.service_models).selectinload(ResearchServiceModel.model)
        )
        
        if service_key:
            query = query.where(ResearchServiceDB.service_key == service_key)
        
        result = await db.execute(query)
        return list(result.scalars().unique())