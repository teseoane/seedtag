from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_radar_endpoint():
    # Prepare the request data
    request_data = {
        'protocols': ['closest-enemies'],
        'scan': [
            {
                'coordinates': {'x': 0, 'y': 100},
                'enemies': {'type': 'mech', 'number': 1},
                'allies': 2
            },
            {
                'coordinates': {'x': 50, 'y': 50},
                'enemies': {'type': 'tank', 'number': 1},
                'allies': None
            },
            {
                'coordinates': {'x': 100, 'y': 0},
                'enemies': {'type': 'mech', 'number': 1},
                'allies': 5
            },
        ]
    }

    # Make the request to the endpoint
    response = client.post('/radar', json=request_data)

    # Check the response status code and data
    assert response.status_code == 200
    assert response.json() == {'x': 50, 'y': 50}
