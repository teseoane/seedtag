from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class Coordinates(BaseModel):
    """Coordinates model to represent the x and y positions of a point."""
    x: int
    y: int


class Enemies(BaseModel):
    """Enemies model to represent the type and number of enemies in a point."""
    type: str
    number: int


class ScanData(BaseModel):
    """ScanData model to represent the information of a scanned point."""
    coordinates: Coordinates
    enemies: Enemies
    allies: Optional[int]


class ProtocolEnum(str, Enum):
    """ProtocolEnum model to define the accepted protocols."""
    AVOID_MECH = 'avoid-mech'
    PRIORITIZE_MECH = 'prioritize-mech'
    AVOID_CROSSFIRE = 'avoid-crossfire'
    ASSIST_ALLIES = 'assist-allies'
    CLOSEST_ENEMIES = 'closest-enemies'
    FURTHEST_ENEMIES = 'furthest-enemies'


class RadarRequest(BaseModel):
    """RadarRequest model to represent the information of a radar request."""
    protocols: List[ProtocolEnum]
    scan: List[ScanData]
