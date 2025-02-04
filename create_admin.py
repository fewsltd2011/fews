from werkzeug.security import generate_password_hash
from models import db, User
import os


def create_admin_account():
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    admin_name = 'Admin User'

    # Check if the admin already exists
    admin = User.query.filter_by(email=admin_email).first()
    if admin:
        print("Admin account already exists.")
        return

    # Create the admin account
    hashed_password = generate_password_hash(admin_password)
    admin = User(
        email=admin_email,
        password=hashed_password,
        name=admin_name
    )

    db.session.add(admin)
    db.session.commit()
    print("Admin account created successfully.")
