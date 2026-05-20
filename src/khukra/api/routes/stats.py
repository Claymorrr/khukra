from fastapi import APIRouter

from khukra.data.engine import get_engine

router = APIRouter()


@router.get("/stats")
def platform_stats() -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        runs = conn.execute("SELECT COUNT(*) FROM simulation_runs").fetchone()[0]
        sweeps = conn.execute("SELECT COUNT(*) FROM parameter_sweeps").fetchone()[0]
        datasets = conn.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
        comparisons = conn.execute("SELECT COUNT(*) FROM run_comparisons").fetchone()[0]
        try:
            inferences = conn.execute("SELECT COUNT(*) FROM inference_events").fetchone()[0]
        except Exception:
            inferences = 0
        try:
            synthetic = conn.execute("SELECT COUNT(*) FROM synthetic_datasets").fetchone()[0]
            artifacts = conn.execute("SELECT COUNT(*) FROM model_artifacts").fetchone()[0]
            evaluations = conn.execute("SELECT COUNT(*) FROM evaluation_runs").fetchone()[0]
        except Exception:
            synthetic = artifacts = evaluations = 0
    return {
        "runs": int(runs),
        "inferences": int(inferences),
        "sweeps": int(sweeps),
        "datasets": int(datasets),
        "comparisons": int(comparisons),
        "synthetic_datasets": int(synthetic),
        "artifacts": int(artifacts),
        "evaluations": int(evaluations),
        "domains": 5,
        "subdomains": 15,
    }
