from flask import Flask
from config import SECRET_KEY, ACCESS_TOKEN_EXP, REFRESH_TOKEN_EXP

from flask_jwt_extended import JWTManager
from web_sockets import socketio

app = Flask(__name__)
socketio.init_app(app, cors_allowed_origins="*")
app.config["JWT_SECRET_KEY"] = SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_TOKEN_EXP
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_TOKEN_EXP

JWT = JWTManager(app)


@app.route("/")
def hello():
    return "Welcome to Farmer APIS"


if __name__ == "__main__":
    # Only for debugging while developing
    socketio.run(app, debug=True)
