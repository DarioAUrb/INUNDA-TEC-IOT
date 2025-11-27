from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, Float
from config.db import meta, engine

users = Table("Lectura_Sensores", meta, 
    Column("id", Integer, primary_key=True), 
    Column("nivel_agua_cm", Float), 
    Column("temperatura_c", Float), 
    Column("humedad_porcentaje", Float))

meta.create_all(engine)