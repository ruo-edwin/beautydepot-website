import os
from sqlalchemy import create_engine, text

host = os.environ["MYSQL_HOST"]
port = os.environ["MYSQL_PORT"]
user = os.environ["MYSQL_USER"]
password = os.environ["MYSQL_PASSWORD"]
database = os.environ["MYSQL_DATABASE"]

url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(url)

with engine.connect() as connection:
    print("RAILWAY MYSQL CONNECTION OK")
    print(connection.execute(text("SELECT 1")).scalar())