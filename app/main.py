from fastapi import FastAPI

from app.schemas import Coordinates, RadarRequest
from app.utils import RadarSystem

app = FastAPI()


@app.post(
    '/radar',
    response_model=Coordinates,
    summary='Find next target',
    description='Receives a RadarRequest JSON data and returns the Coordinates of the visible objective to attack.',
    tags=['radar'],
    responses={
        200: {
            'description': 'Successful response',
            'content': {'application/json': {'example': {'latitude': 12.34, 'longitude': 56.78}}},
        },
        422: {'description': 'Validation error'},
    },
)
async def radar(request: RadarRequest) -> Coordinates:
    """Endpoint that receives a RadarRequest JSON data and returns the Coordinates
    of the visible objective to attack.

    Args:
        request (RadarRequest): The radar request sent to the endpoint.

    Returns:
        Coordinates: The coordinates of the next point to attack.
    """
    radar_system = RadarSystem(request.protocols)
    return radar_system.find_next_target(request.scan)
