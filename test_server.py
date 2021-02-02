import pytest
from main import create_app


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    """Get client instance from app for tests"""
    return app.test_client()


def test_process_bot_message(client):
    request_data = {"value": "Червяки: Егор 1, Саша 5, Сергей 0, Юля 3"}
    response = client.post('/webhooks/stats', json=request_data)
    print(response)
    assert response.json == request_data
