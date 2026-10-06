from getpass import getpass

from passlib.context import CryptContext

from backend.db import SessionLocal
from backend import models


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def main():

    db = SessionLocal()

    try:

        print("\n=== Create Admin Account ===\n")

        name = input("Admin name: ").strip()
        email = input("Admin email: ").strip().lower()

        password = getpass("Admin password: ")
        confirm_password = getpass("Confirm password: ")

        if not name:
            print("Name is required.")
            return

        if not email:
            print("Email is required.")
            return

        if not password:
            print("Password is required.")
            return

        if password != confirm_password:
            print("Passwords do not match.")
            return

        existing_admin = db.query(models.Admin).filter(
            models.Admin.email == email
        ).first()

        if existing_admin:
            print("An admin with this email already exists.")
            return

        password_hash = pwd_context.hash(password)

        admin = models.Admin(
            name=name,
            email=email,
            password_hash=password_hash,
            is_active=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\nAdmin account created successfully!")
        print(f"Admin ID: {admin.id}")
        print(f"Email: {admin.email}")

    finally:

        db.close()


if __name__ == "__main__":
    main()