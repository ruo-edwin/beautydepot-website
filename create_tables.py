from backend.db import engine, Base
from backend import models


print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Database tables created successfully.")