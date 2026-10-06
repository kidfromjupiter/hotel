from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import bcrypt
import jwt

from app.repositories.staff_repo import StaffRepo


class AuthService:
    def __init__(
        self,
        repo: StaffRepo,
        secret_key: str,
        algorithm: str = "HS256",
        expire_minutes: int = 720,
    ) -> None:
        self.repo = repo
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a bcrypt hash string."""
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except Exception:
            return False

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """Hash a plaintext password using bcrypt with salt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")

    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a signed JWT token containing user identity and expiration."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=self.expire_minutes)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and validate a JWT token signature and expiration."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
            )
            return payload
        except jwt.PyJWTError:
            return None

    def authenticate_user(
        self,
        username: str,
        password: str,
    ) -> Optional[Dict[str, Any]]:
        """Verify username & password against database records."""
        user = self.repo.get_by_username(username)
        if not user:
            return None
        if not user.get("is_active"):
            return None
        if not self.verify_password(password, user["password_hash"]):
            return None
        return user
