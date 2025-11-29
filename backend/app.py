from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.devices import sensor
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las direcciones 
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos los headers
)

app.include_router(sensor)