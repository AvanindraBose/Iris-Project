# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture(scope="session")
def client():
    return TestClient(app)

