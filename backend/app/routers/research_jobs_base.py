# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from app.schemas.research_job import ResearchJob
from app.schemas.research_job_create_request import ResearchJobCreateRequest


class BaseResearchJobs:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseResearchJobs.subclasses = BaseResearchJobs.subclasses + (cls,)
    async def research_jobs_job_id_get(
        self,
        job_id: StrictStr,
    ) -> ResearchJob:
        ...


    async def research_jobs_post(
        self,
        research_job_create_request: ResearchJobCreateRequest,
    ) -> ResearchJob:
        ...
