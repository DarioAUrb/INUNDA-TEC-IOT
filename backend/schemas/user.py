from pydantic import BaseModel
from typing import Optional
from datetime import datetime
class Lectura_Sensores(BaseModel): 
    id: Optional[str] = None
    nivel_agua_cm: float
    temperatura_c: float
    humedad_porcentaje: float
    fecha_registro: Optional[datetime] = None
    