from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:root1234@localhost:3306/inunda_tec")


meta = MetaData()

conn = engine.connect()