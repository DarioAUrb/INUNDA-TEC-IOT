from sqlalchemy import Table, Column
from sqlalchemy import String, Float, TIMESTAMP, func
from sqlalchemy.dialects.mysql import VARCHAR
from config.db import meta, engine
import uuid

Sensors = Table("Sensor_Readings", meta, 
    Column("id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    Column("water_level_cm", Float), 
    Column("temperature_c", Float), 
    Column("humidity_percentage", Float),
    Column("registration_date", TIMESTAMP, server_default=func.now()))

meta.create_all(engine)