from flask import Flask

from .auth_login import auth_login
from .auth_logout import auth_logout
from .auth_signup import auth_signup
from .health import health
from .medicine_type import medicine_type

app = Flask(__name__)
app.register_blueprint(health)
app.register_blueprint(auth_login)
app.register_blueprint(auth_signup)
app.register_blueprint(auth_logout)
app.register_blueprint(medicine_type)


if __name__ == "__main__":
    app.run(port=5010)
