import os

from khukra.auth.security import hash_password
from khukra.data.repositories.users import UserRepository


def ensure_default_admin() -> None:
    """Create default team admin if no users exist."""
    repo = UserRepository()
    email = os.getenv("KHUKRA_ADMIN_EMAIL", "admin@khukra.local")
    if repo.get_by_email(email):
        return

    password = os.getenv("KHUKRA_ADMIN_PASSWORD", "khukra-admin")
    repo.create(
        email=email,
        display_name="Khukra Admin",
        password_hash=hash_password(password),
        role="admin",
    )
