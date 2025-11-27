from fastapi import APIRouter
from config.db import conn
from models.user import users
from schemas.user import Lectura_Sensores
from cryptography.fernet import Fernet

user = APIRouter()
Key = Fernet.generate_key()
f = Fernet(Key)

@user.post("/users")
def createSensorData(data: Lectura_Sensores):
    new_data = {"id": data.id, "nivel_agua_cm": data.nivel_agua_cm, "temperatura_c": data.temperatura_c, "humedad_porcentaje": data.humedad_porcentaje}
    result = conn.execute(users.insert().values(new_data))
    conn.commit()
    print (result)
    return "received"
    
@user.get("/users")
def get_users():
    result = conn.execute(users.select())
    return result.fetchall()