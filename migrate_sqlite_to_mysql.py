import os

from sqlalchemy import create_engine, MetaData, select, text, Text

from sqlalchemy.engine import URL


# ============================================================
# 1. SQLITE SOURCE
# ============================================================

sqlite_engine = create_engine(
    "sqlite:///./beauty_ecommerce.db"
)

from sqlalchemy import String

source_metadata = MetaData()
source_metadata.reflect(bind=sqlite_engine)

# SQLite allows VARCHAR without a length.
# MySQL requires VARCHAR to have a length.
for table in source_metadata.tables.values():
    for column in table.columns:
        if isinstance(column.type, String) and column.type.length is None:
            column.type = Text()

print("SQLite tables found:")
for table in source_metadata.sorted_tables:
    print(f"  - {table.name}")


# ============================================================
# 2. RAILWAY MYSQL CONNECTION
# ============================================================

mysql_url = URL.create(
    drivername="mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ["MYSQL_HOST"],
    port=int(os.environ["MYSQL_PORT"]),
    database=os.environ["MYSQL_DATABASE"],
)

mysql_engine = create_engine(mysql_url)


# ============================================================
# 3. TEST MYSQL
# ============================================================

with mysql_engine.connect() as connection:
    connection.execute(text("SELECT 1"))

print("\nRailway MySQL connection OK.")


# ============================================================
# 4. CREATE TABLES
# ============================================================

print("\nCreating MySQL tables...")

source_metadata.create_all(mysql_engine)

print("MySQL tables created.")


# ============================================================
# 5. COPY DATA
# ============================================================

print("\nStarting data migration...")

with sqlite_engine.connect() as sqlite_connection:
    with mysql_engine.begin() as mysql_connection:

        # Temporarily disable foreign-key checks while importing.
        mysql_connection.execute(
            text("SET FOREIGN_KEY_CHECKS = 0")
        )

        for table in source_metadata.sorted_tables:

            rows = sqlite_connection.execute(
                select(table)
            ).mappings().all()

            if not rows:
                print(f"{table.name}: 0 rows")
                continue

            # Convert RowMapping objects to normal dictionaries.
            data = [dict(row) for row in rows]

            mysql_connection.execute(
                table.insert(),
                data
            )

            print(f"{table.name}: {len(data)} rows copied")

        mysql_connection.execute(
            text("SET FOREIGN_KEY_CHECKS = 1")
        )


# ============================================================
# 6. VERIFY COUNTS
# ============================================================

print("\nMigration complete.")
print("\nVerifying MySQL row counts...")

with mysql_engine.connect() as connection:

    for table in source_metadata.sorted_tables:

        result = connection.execute(
            text(f"SELECT COUNT(*) FROM `{table.name}`")
        ).scalar()

        print(f"{table.name}: {result}")

print("\nDONE.")