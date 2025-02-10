import os

import pytest


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables before each test"""
    os.environ["JWT_SECRET_KEY"] = "test_secret"
    os.environ["CONTAINER_ID"] = "test_container_123"
    yield
