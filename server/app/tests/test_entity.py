import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_list_entities(client):
    response = client.get('/api/entities/')
    assert response.status_code == 200
    assert isinstance(response.get_json(), list) 