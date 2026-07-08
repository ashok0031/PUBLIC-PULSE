import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_rating(client):
    response = client.get('/api/ratings/1')
    assert response.status_code in (200, 404) 