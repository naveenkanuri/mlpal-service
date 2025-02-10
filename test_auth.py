import os
from datetime import datetime, timedelta

import jwt
import pytest
from fastapi import HTTPException

from auth import AuthHandler


class TestAuthHandler:
    def setup_method(self):
        # Setup test environment variables
        import os

        os.environ["JWT_SECRET_KEY"] = "test_secret"
        os.environ["CONTAINER_ID"] = "test_container_123"
        self.auth_handler = AuthHandler()

    def create_test_token(
        self, user_id="test_user", container_id="test_container_123", expired=False
    ):
        payload = {
            "user_id": user_id,
            "container_id": container_id,
            "exp": datetime.utcnow()
            + (timedelta(days=-1) if expired else timedelta(days=1)),
        }
        return jwt.encode(payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256")

    def test_valid_token_decode(self):
        token = self.create_test_token()
        decoded = self.auth_handler.decode_token(token)
        assert decoded["user_id"] == "test_user"
        assert decoded["container_id"] == "test_container_123"

    def test_expired_token(self):
        token = self.create_test_token(expired=True)
        with pytest.raises(HTTPException) as exc_info:
            self.auth_handler.decode_token(token)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token has expired"

    def test_invalid_container_id(self):
        token = self.create_test_token(container_id="wrong_container")
        with pytest.raises(HTTPException) as exc_info:
            self.auth_handler.decode_token(token)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid container access"
