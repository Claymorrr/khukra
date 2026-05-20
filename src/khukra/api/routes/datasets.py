from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from khukra.api.schemas import DatasetInfo, IngestResponse
from khukra.auth.deps import get_current_user, require_user
from khukra.data.engine import get_engine
from khukra.data.pipeline.ingest import IngestPipeline
from khukra.data.repositories.datasets import DatasetRepository

router = APIRouter()
pipeline = IngestPipeline()
datasets_repo = DatasetRepository()


@router.get("/datasets", response_model=list[DatasetInfo])
def list_datasets(domain_tag: str | None = None) -> list[DatasetInfo]:
    records = datasets_repo.list_all(domain_tag=domain_tag)
    return [
        DatasetInfo(
            dataset_id=r["dataset_id"],
            name=r["name"],
            source_type=r["source_type"],
            row_count=r["row_count"],
            domain_tag=r.get("domain_tag"),
            created_at=r["created_at"].isoformat() if hasattr(r["created_at"], "isoformat") else str(r["created_at"]),
        )
        for r in records
    ]


@router.post("/datasets/ingest", response_model=IngestResponse)
async def ingest_dataset(
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    domain_tag: str | None = Form(default=None),
    transform: str | None = Form(default=None),
    user: dict = Depends(require_user),
) -> IngestResponse:
    engine = get_engine()
    temp_path = engine.datasets_dir / f"upload_{file.filename}"
    content = await file.read()
    temp_path.write_bytes(content)

    try:
        result = pipeline.ingest_file(
            temp_path,
            name=name or file.filename,
            domain_tag=domain_tag,
            user_id=user["user_id"],
            transform=transform,
        )
        return IngestResponse(**result)
    except Exception as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str) -> dict:
    meta = datasets_repo.get(dataset_id)
    if not meta:
        raise HTTPException(404, "Dataset not found")
    profile = pipeline.profile_dataset(dataset_id)
    return {**meta, "profile": profile}


@router.get("/datasets/{dataset_id}/preview")
def preview_dataset(dataset_id: str, rows: int = 20) -> dict:
    df = datasets_repo.load_dataframe(dataset_id)
    return {"columns": list(df.columns), "rows": df.head(rows).to_dict(orient="records")}
