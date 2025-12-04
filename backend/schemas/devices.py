from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

class SensorReading(BaseModel): 
    id: Optional[str] = None
    water_level_cm: float
    temperature_c: float
    humidity_percentage: float
    registration_date: Optional[datetime] = None
    

class Phone(BaseModel):
    phone_number: str
    owner_name: Optional[str] = None
    is_active: Optional[bool] = True
    
    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        # Basic validation: must start with + and contain only digits after that
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if not v[1:].isdigit():
            raise ValueError('Phone number must contain only digits after +')
        if len(v) < 10:
            raise ValueError('Phone number too short')
        return v

class AlertPhoneResponse(Phone):
    id: str
    created_date: datetime