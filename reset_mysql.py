import os

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


mysql_url = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ["MYSQL_PORT"]),
    database=os.environ["MYSQL_DATABASE"],
)

engine = create_engine(mysql_url)

tables = [
    "order_items",
    "orders",
    "products",
    "subcategories",
    "categories",
    "brands",
    "admins",
]

with engine.begin() as connection:
    connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    for table in tables:
        connection.execute(text(f"DROP TABLE IF EXISTS `{table}`"))
        print(f"Dropped: {table}")

    connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

print("\nRailway MySQL is clean.")