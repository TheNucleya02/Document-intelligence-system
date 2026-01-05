from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel
import time

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Job(BaseModel):
    id: str
    status: JobStatus
    created_at: float = time.time()
    result: Dict[str, Any] = None
    error: str = None

# In-memory database
# { "job_uuid": Job(...) }
job_store: Dict[str, Job] = {}

def create_job(job_id: str) -> Job:
    job = Job(id=job_id, status=JobStatus.PENDING)
    job_store[job_id] = job
    return job

def get_job(job_id: str) -> Job:
    return job_store.get(job_id)

def update_job_status(job_id: str, status: JobStatus, result: dict = None, error: str = None):
    if job_id in job_store:
        job_store[job_id].status = status
        if result:
            job_store[job_id].result = result
        if error:
            job_store[job_id].error = error