import os
from pathlib import Path

import duckdb

from khukra.data.migrations import apply_migrations


def _default_root() -> Path:
    return Path(os.environ.get("KHUKRA_DATA_ROOT", "data"))


class DataEngine:
    """Central DuckDB warehouse for inference runs, datasets, sweeps, and auth."""

    def __init__(self, root: Path | str | None = None):
        root = root or _default_root()
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "warehouse").mkdir(exist_ok=True)
        (self.root / "datasets").mkdir(exist_ok=True)
        (self.root / "exports").mkdir(exist_ok=True)
        (self.root / "runs").mkdir(exist_ok=True)
        (self.root / "synthetic").mkdir(exist_ok=True)
        (self.root / "features").mkdir(exist_ok=True)
        (self.root / "artifacts").mkdir(exist_ok=True)
        self.db_path = self.root / "warehouse" / "khukra.duckdb"
        apply_migrations(self.db_path)

    def connect(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    @property
    def datasets_dir(self) -> Path:
        return self.root / "datasets"

    @property
    def exports_dir(self) -> Path:
        return self.root / "exports"

    @property
    def runs_dir(self) -> Path:
        return self.root / "runs"


_engine: DataEngine | None = None


def get_engine(root: Path | str | None = None) -> DataEngine:
    global _engine
    if _engine is None or root is not None:
        _engine = DataEngine(root or _default_root())
    return _engine
