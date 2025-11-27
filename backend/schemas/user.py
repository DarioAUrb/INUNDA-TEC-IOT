from pydantic import BaseModel

class Lectura_Sensores(BaseModel): 
    id: str
    nivel_agua_cm: str
    temperatura_c: str
    humedad_porcentaje: str
    