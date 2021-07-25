"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from flask_restplus import Resource

from webserver.core.portofolio_management import PortofolioManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.authentication import token_required
from webserver.routes.utils import api_param_query, api_param_form, get_request_parameter

api = FlaskRestPlusApi.get_instance()


class RoutePortofolio(Resource):

    @staticmethod
    @api.doc(params={
        "portofolio_id": api_param_query(required=False,
                                         description="Portofolio id"),
    })
    @api.doc(responses={
        # TODO
        200: "OK",
    })
    @token_required
    def get(current_user) -> response:
        portofolio_id = get_request_parameter(name="portofolio_id", expected_type=str, required=False)
        return response(*PortofolioManagementAPI.get_portofolio(current_user.public_id, portofolio_id))

    @staticmethod
    @api.doc(params={
        "portofolio_name": api_param_form(required=False, description='Portofolio name'),
        "allocations": api_param_form(required=True, description="Portofolio allocations")
    })
    @api.doc(responses={
        # TODO
        201: "OK",
    })
    @token_required
    def post(current_user) -> response:
        portofolio_name = get_request_parameter('portofolio_name', required=False, expected_type=str)

        allocations, msg = get_request_parameter('allocations', required=True, expected_type=list)
        if not allocations:
            return response_400(msg)

        return response(*PortofolioManagementAPI.create_portofolio(user_id=current_user.public_id,
                                                                   allocations=allocations,
                                                                   portofolio_name=portofolio_name))

    @staticmethod
    @api.doc(params={
        "portofolio_name": api_param_form(required=False, description='Portofolio name'),
        "portofolio_id": api_param_form(required=True, description="Portofolio id"),
        "allocations": api_param_form(required=True, description="Portofolio allocations")
    })
    @api.doc(responses={
        # TODO
        201: "OK",
    })
    @token_required
    def put(current_user) -> response:
        portofolio_name = get_request_parameter(name='portofolio_name', required=False, expected_type=str)

        portofolio_id, msg = get_request_parameter(name='portofolio_id', required=True, expected_type=str)
        if not portofolio_id:
            return response_400(msg)

        allocations, msg = get_request_parameter(name='allocations', required=True, expected_type=list)
        if not allocations:
            return response_400(msg)

        return response(*PortofolioManagementAPI.update_portofolio(user_id=current_user.public_id,
                                                                   portofolio_id=portofolio_id,
                                                                   allocations=allocations,
                                                                   portofolio_name=portofolio_name))

    @staticmethod
    @api.doc(params={
        "portofolio_id": api_param_query(required=True, description="Portofolio id")
    })
    @api.doc(responses={
        # TODO
        200: "OK",
    })
    @token_required
    def delete(current_user) -> response:
        portofolio_id, msg = get_request_parameter(name="portofolio_id", expected_type=str, required=True)
        if not portofolio_id:
            return response_400(msg)
        return response(*PortofolioManagementAPI.delete_portofolio(user_id=current_user.public_id,
                                                                   portofolio_id=portofolio_id))


class RouteBacktest(Resource):
    # TODO
    pass
