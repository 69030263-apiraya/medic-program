from flask import current_app
from werkzeug.security import check_password_hash


def verify_password(stored_password: str, password: str) -> bool:
    if stored_password.startswith(("scrypt:", "pbkdf2:")):
        try:
            return check_password_hash(stored_password, password)
        except ValueError:
            current_app.logger.error("A user record contains an invalid password hash.")
            return False

    return stored_password == password
