from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorReading(BaseModel): 
    id: Optional[str] = None
    water_level_cm: float
    temperature_c: float
    humidity_percentage: float
    registration_date: Optional[datetime] = None