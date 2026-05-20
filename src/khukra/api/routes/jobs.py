from fastapi import APIRouter, HTTPException

from khukra.data.repositories.jobs import JobRepository

router = APIRouter(prefix="/jobs")
_repo = JobRepository()


@router.get("")
def list_jobs(job_type: str | None = None, limit: int = 50) -> dict:
    return {"jobs": _repo.list_jobs(job_type=job_type, limit=limit)}


@router.get("/{job_id}")
def get_job(job_id: str) -> dict:
    job = _repo.get(job_id)
    if not job:
        raise HTTPException(404, f"Job not found: {job_id}")
    return job
