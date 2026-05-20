import uuid
from datetime import datetime, timezone
from typing import Any

from khukra.data.engine import DataEngine, get_engine


class UserRepository:
    def __init__(self, engine: DataEngine | None = None):
        self.engine = engine or get_engine()

    def create(
        self,
        email: str,
        display_name: str,
        password_hash: str,
        role: str = "analyst",
    ) -> str:
        user_id = str(uuid.uuid4())[:12]
        with self.engine.connect() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, email, display_name, password_hash, role, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, TRUE)
                """,
                [user_id, email.lower(), display_name, password_hash, role, datetime.now(timezone.utc)],
            )
        return user_id

    def get_by_email(self, email: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM users WHERE email = ? AND is_active = TRUE",
                [email.lower()],
            ).fetchdf()
        if df.empty:
            return None
        return self._row(df.iloc[0])

    def get_by_id(self, user_id: str) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            df = conn.execute(
                "SELECT * FROM users WHERE user_id = ?", [user_id]
            ).fetchdf()
        if df.empty:
            return None
        return self._row(df.iloc[0])

    def count(self) -> int:
        with self.engine.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM users").fetchone()[0])

    @staticmethod
    def _row(row) -> dict[str, Any]:
        return {
            "user_id": row["user_id"],
            "email": row["email"],
            "display_name": row["display_name"],
            "password_hash": row["password_hash"],
            "role": row["role"],
            "created_at": row["created_at"],
        }
