'''Main view.'''
from fastapi import FastAPI

from app.models import Coordinates, RadarRequest
from app.utils import RadarSystem

app = FastAPI()


@app.post('/radar', response_model=Coordinates)
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
