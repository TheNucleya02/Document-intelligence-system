from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel
import time
from app.db.session import SessionLocal
from app.db.models import Job as JobModel
import json

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

def create_job(job_id: str) -> Job:
    db = SessionLocal()
    try:
        job = JobModel(id=job_id, status=JobStatus.PENDING)
        db.add(job)
        db.commit()
        return Job(id=job.id, status=job.status, created_at=time.time())
    finally:
        db.close()

def get_job(job_id: str) -> Job:
    db = SessionLocal()
    try:
        job = db.query(JobModel).filter(JobModel.id == job_id).first()
        if job:
            result = json.loads(job.result) if job.result else None
            return Job(
                id=job.id,
                status=job.status,
                result=result,
                error=job.error,
                created_at=job.created_at.timestamp()
            )
        return None
    finally:
        db.close()

def update_job_status(job_id: str, status: JobStatus, result: dict = None, error: str = None):
    db = SessionLocal()
    try:
        job = db.query(JobModel).filter(JobModel.id == job_id).first()
        if job:
            job.status = status
            if result:
                job.result = json.dumps(result)
            if error:
                job.error = error
            db.commit()
    finally:
        db.close()