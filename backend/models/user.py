from sqlalchemy import Table, Column
from sqlalchemy import String, Float, TIMESTAMP, func
from config.db import meta, engine

users = Table("Lectura_Sensores", meta, 
    Column("id", String, primary_key=True),
    Column("nivel_agua_cm", Float), 
    Column("temperatura_c", Float), 
    Column("humedad_porcentaje", Float),
    Column("fecha_registro", TIMESTAMP, server_default=func.now()))

meta.create_all(engine)