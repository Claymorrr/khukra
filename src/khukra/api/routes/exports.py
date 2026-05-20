from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from khukra.data.export.exporter import ExportService

router = APIRouter()
exporter = ExportService()


@router.get("/export/runs.csv")
def export_runs_csv(run_ids: str = Query(..., description="Comma-separated run IDs")):
    ids = [r.strip() for r in run_ids.split(",") if r.strip()]
    path = exporter.export_runs_csv(ids)
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/export/runs/{run_id}/series.csv")
def export_series_csv(run_id: str):
    path = exporter.export_run_series_csv(run_id)
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/export/comparisons/{comparison_id}.csv")
def export_comparison_csv(comparison_id: str):
    path = exporter.export_comparison_csv(comparison_id)
    return FileResponse(path, filename=path.name, media_type="text/csv")


@router.get("/export/report.pdf")
def export_report_pdf(
    title: str = Query(default="Khukra Inference Report"),
    run_ids: str | None = Query(default=None),
    comparison_id: str | None = Query(default=None),
):
    ids = [r.strip() for r in run_ids.split(",")] if run_ids else None
    path = exporter.export_report_pdf(title, ids, comparison_id)
    return FileResponse(path, filename=path.name, media_type="application/pdf")
