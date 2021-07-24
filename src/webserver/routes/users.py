"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from flask_restplus import Resource
from werkzeug.security import generate_password_hash

from webserver.core.users_management import UsersManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.utils import api_param_form, get_request_parameter, api_param_query

api = FlaskRestPlusApi.get_instance()


class RouteUsers(Resource):

    @api.doc(params={
        "public_id": api_param_query(required=False, description="User id")
    })
    @api.doc(responses={
        200: "OK",
        404: "User not found."
    })
    def get(self) -> response:
        public_id = get_request_parameter('public_id', required=False, expected_type=str)
        return response(*UsersManagementAPI.get_users(public_id=public_id))

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
    def post(self) -> response:
        username, msg = get_request_parameter(name="username", expected_type=str, required=True)
        if not username:
            return response_400(msg)

        password, msg = get_request_parameter(name="password", expected_type=str, required=True)
        if not password:
            return response_400(msg)

        if len(password) <= 3:
            return response_400("Password must have more than 3 characters")

        hashed_password = generate_password_hash(password=password, method='sha256')

        return response(*UsersManagementAPI.create_user(username=username, hashed_password=hashed_password))

    @api.doc(params={
        "public_id": api_param_query(required=True, description="Public user id"),
    })
    @api.doc(responses={
        201: "OK",
        400: "Param <> is required",
        404: "User not found."
    })
    def put(self) -> response:
        public_id, msg = get_request_parameter('public_id', required=True, expected_type=str)
        if not public_id:
            return response_400(msg)

        return response(*UsersManagementAPI.promote_user(public_id=public_id))

    @api.doc(params={
        "public_id": api_param_query(required=True, description="Public user id"),
    })
    @api.doc(responses={
        200: "OK",
        400: "Param <> is required",
        404: "User not found."
    })
    def delete(self) -> response:
        public_id, msg = get_request_parameter('public_id', required=True, expected_type=str)
        if not public_id:
            return response_400(msg)

        return response(*UsersManagementAPI.delete_use(public_id=public_id))
