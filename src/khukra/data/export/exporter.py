import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from khukra.data.engine import DataEngine, get_engine
from khukra.data.repositories.comparisons import ComparisonRepository
from khukra.data.repositories.runs import RunRepository


class ExportService:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()
        self.runs = RunRepository(self.engine)
        self.comparisons = ComparisonRepository(self.engine)

    def export_runs_csv(self, run_ids: list[str]) -> Path:
        rows = []
        for rid in run_ids:
            run = self.runs.get(rid)
            if not run:
                continue
            for metric, value in run["metrics"].items():
                rows.append({
                    "run_id": rid,
                    "domain": run["domain"],
                    "subdomain": run["subdomain"],
                    "model_name": run["model_name"],
                    "metric": metric,
                    "value": value,
                })
        df = pd.DataFrame(rows)
        out = self._export_path("runs", "csv")
        df.to_csv(out, index=False)
        return out

    def export_run_series_csv(self, run_id: str) -> Path:
        series = self.runs.load_series(run_id)
        if series is None:
            raise FileNotFoundError("No series for run")
        out = self._export_path(f"series_{run_id}", "csv")
        series.to_csv(out, index=False)
        return out

    def export_sweep_csv(self, run_ids: list[str]) -> Path:
        return self.export_runs_csv(run_ids)

    def export_comparison_csv(self, comparison_id: str) -> Path:
        comp = self.comparisons.get(comparison_id)
        if not comp:
            raise FileNotFoundError("Comparison not found")
        df = pd.DataFrame(comp["summary"].get("metrics_table", []))
        out = self._export_path(f"comparison_{comparison_id}", "csv")
        df.to_csv(out, index=False)
        return out

    def export_report_pdf(
        self,
        title: str,
        run_ids: list[str] | None = None,
        comparison_id: str | None = None,
    ) -> Path:
        from matplotlib.backends.backend_pdf import PdfPages
        import matplotlib.pyplot as plt

        out = self._export_path("report", "pdf")
        with PdfPages(out) as pdf:
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            ax.text(0.5, 0.9, "Khukra Analytics Report", ha="center", fontsize=18, fontweight="bold")
            ax.text(0.5, 0.82, title, ha="center", fontsize=12)
            ax.text(0.5, 0.75, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), ha="center", fontsize=9)
            pdf.savefig(fig)
            plt.close(fig)

            if comparison_id:
                comp = self.comparisons.get(comparison_id)
                if comp:
                    self._pdf_table_page(pdf, "Comparison Summary", comp["summary"].get("delta", {}))

            if run_ids:
                for rid in run_ids[:6]:
                    run = self.runs.get(rid)
                    if run:
                        self._pdf_table_page(pdf, f"Run {rid} — {run['model_name']}", run["metrics"])
                    series = self.runs.load_series(rid)
                    if series is not None and len(series.columns) >= 2:
                        fig, ax = plt.subplots(figsize=(8.5, 4))
                        x_col = series.columns[0]
                        for col in series.columns[1:]:
                            ax.plot(series[x_col], series[col], label=col)
                        ax.legend(fontsize=8)
                        ax.set_title(f"Series — {rid}")
                        ax.grid(True, alpha=0.3)
                        pdf.savefig(fig)
                        plt.close(fig)

        return out

    def _pdf_table_page(self, pdf, title: str, data: dict[str, Any]) -> None:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8.5, 6))
        ax.axis("off")
        ax.set_title(title, fontsize=12, fontweight="bold")
        if not data:
            ax.text(0.1, 0.5, "No data", fontsize=10)
        else:
            lines = []
            for k, v in data.items():
                if isinstance(v, dict):
                    lines.append(f"{k}: {json.dumps(v)}")
                else:
                    lines.append(f"{k}: {v}")
            ax.text(0.05, 0.85, "\n".join(lines[:25]), va="top", fontsize=9, family="monospace")
        pdf.savefig(fig)
        plt.close(fig)

    def _export_path(self, prefix: str, ext: str) -> Path:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = self.engine.exports_dir / f"{prefix}_{ts}.{ext}"
        return path
