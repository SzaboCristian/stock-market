"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import datetime
from functools import wraps

import jwt
from flask import request
from flask_restplus import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from webserver.core.users_management import UsersManagementAPI
from webserver.flask_rest import FlaskRestPlusApi, FlaskApp
from webserver.models.user import User
from webserver.responses import response_400, response
from webserver.routes.utils import api_param_form, get_request_parameter

api = FlaskRestPlusApi.get_instance()
app = FlaskApp.get_instance()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return response(401, {}, 'Token is missing')

        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return response(401, {}, 'Invalid token.')

        return f(current_user, *args, **kwargs)

    return decorated


class RouteLogin(Resource):

    @staticmethod
    @api.doc(responses={
        201: "OK",
        401: "Could not verify authorization."
    })
    def post() -> response:
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return response(401, {'WWW-Authenticate': 'Basic realm="Login required!"'},
                            'Could not verify authorization.')

        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return response(401, {'WWW-Authenticate': 'Basic realm="Login required!"'},
                            'Could not verify authorization.')

        if not check_password_hash(user.password, auth.password):
            return response(401, {'WWW-Authenticate': 'Basic realm="Login required!"'},
                            'Could not verify authorization.')

        token = jwt.encode(
            {'public_id': user.public_id,
             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60)},
            app.config["SECRET_KEY"])

        return response(201, {'token': token.decode('UTF-8')}, 'OK')


class RouteRegister(Resource):

    @staticmethod
    @api.doc(params={
        "username": api_param_form(required=True, description="Username"),
        "password": api_param_form(required=True, description="Password"),
    })
    @api.doc(responses={
        201: "OK",
        400: "Param <> is required | Password must have more than 3 characters",
        409: "Username already exists.",
        500: "Could not create user."
    })
    def post() -> response:
        username, msg = get_request_parameter(name="username", expected_type=str, required=True)
        if not username:
            return response_400(msg)

        password, msg = get_request_parameter(name="password", expected_type=str, required=True)
        if not password:
            return response_400(msg)
        hashed_password = generate_password_hash(password=password, method='sha256')
        return response(*UsersManagementAPI.create_user(username=username, hashed_password=hashed_password))
