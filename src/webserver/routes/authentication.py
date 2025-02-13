"""
API Route class.
"""

import datetime
from functools import wraps

import jwt
from flask import request
from flask_restplus import Resource
from werkzeug.security import check_password_hash

from webserver import decorators
from webserver.flask_rest import FlaskApp, FlaskRestPlusApi
from webserver.model.user import User
from webserver.responses import response

api = FlaskRestPlusApi.get_instance()
app = FlaskApp.get_instance()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return response(401, {}, "Token is missing")

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(public_id=data["public_id"]).first()
        except:
            return response(401, {}, "Invalid token.")

        return f(current_user, *args, **kwargs)

    return decorated


class RouteLogin(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(description="Log in and get JWT.")
    @api.doc(responses={201: "OK", 401: "Could not verify authorization."})
    @api.doc(security="Basic Auth")
    def post() -> response:
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return response(
                401,
                {"WWW-Authenticate": 'Basic realm="Login required!"'},
                "Could not verify authorization.",
            )

        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return response(
                401,
                {"WWW-Authenticate": 'Basic realm="Login required!"'},
                "Invalid username.",
            )

        if not check_password_hash(user.password, auth.password):
            return response(
                401,
                {"WWW-Authenticate": 'Basic realm="Login required!"'},
                "Invalid password.",
            )

        token = jwt.encode(
            {
                "public_id": user.public_id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            },
            app.config["SECRET_KEY"],
        )

        return response(201, {"token": token.decode("UTF-8")}, "OK")
