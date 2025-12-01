from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.pool import NullPool

engine = create_engine(
    "mysql+pymysql://root:root1234@localhost:3306/inunda_tec",
    poolclass=NullPool
)

meta = MetaData()

# Crear conexión con mejor manejo de errores
def get_connection():
    try:
        conn = engine.connect()
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

conn = get_connection()