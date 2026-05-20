"""Legacy ResultsStore — delegates to RunRepository for backward compatibility."""

from khukra.data.repositories.runs import RunRepository


class ResultsStore(RunRepository):
    """Alias for RunRepository; uses data/runs paths via engine."""

    def list_runs(self, domain: str | None = None):
        import pandas as pd

        records = self.list_runs(domain=domain)
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        df = df.rename(columns={"created_at": "timestamp"})
        return df
