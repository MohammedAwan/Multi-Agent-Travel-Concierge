import pytest
import os

# Set mock env vars before importing application modules
os.environ["JWT_SECRET_KEY"] = "test-secret-key-32-chars-long-minimum"
os.environ["GROQ_API_KEY"] = "gsk_mock_test_key"
os.environ["OPENWEATHER_API_KEY"] = "mock_weather_key"

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token, hash_password

@pytest.fixture
def test_user_id():
    return 42

@pytest.fixture
def valid_jwt_token(test_user_id):
    """Generates a valid JWT token signed with the test secret."""
    return create_access_token({"sub": str(test_user_id)})

@pytest.fixture
async def async_client():
    """Async client to test FastAPI endpoints without booting a real socket."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client