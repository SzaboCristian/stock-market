"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time

from flask_restplus import Resource

from webserver import decorators
from webserver.core.portfolio_management import PortfolioManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.authentication import token_required
from webserver.routes.utils import api_param_query, api_param_form, get_request_parameter

api = FlaskRestPlusApi.get_instance()

FIVE_YEARS_TS = int(time.time()) - 5 * 365 * 24 * 3600


class RoutePortfolio(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(params={
        "portfolio_id": api_param_query(required=False,
                                        description="Portfolio id"),
    })
    @api.doc(responses={
        200: "OK",
        404: "User not found. | Portfolio not found."
    })
    @api.doc(security='apiKey')
    @token_required
    def get(current_user) -> response:
        portfolio_id = get_request_parameter(name="portfolio_id", expected_type=str, required=False)
        return response(*PortfolioManagementAPI.get_portfolio(current_user.public_id, portfolio_id))

    @staticmethod
    @api.doc(params={
        "portfolio_name": api_param_form(required=False, description='Portfolio name'),
        "allocations": api_param_form(required=True,
                                      description="Portfolio allocations. Json list of dicts; "
                                                  "format [{\"ticker\": <ticker>, \"percentage\": <int>}]")
    })
    @api.doc(responses={
        201: "OK",
        400: "Invalid allocation <> | Total allocation percentage must be 100%.",
        404: "User not found.",
        500: "Could not create portfolio."
    })
    @api.doc(security='apiKey')
    @token_required
    def post(current_user) -> response:
        portfolio_name = get_request_parameter('portfolio_name', required=False, expected_type=str)

        allocations, msg = get_request_parameter('allocations', required=True, expected_type=list)
        if not allocations:
            return response_400(msg)

        return response(*PortfolioManagementAPI.create_portfolio(user_id=current_user.public_id,
                                                                 allocations=allocations,
                                                                 portfolio_name=portfolio_name))

    @staticmethod
    @api.doc(params={
        "portfolio_name": api_param_form(required=False, description='Portfolio name'),
        "portfolio_id": api_param_form(required=True, description="Portfolio id"),
        "allocations": api_param_form(required=True, description="Portfolio allocations")
    })
    @api.doc(responses={
        201: "OK",
        400: "Invalid allocation <>",
        401: "Cannot update other users\' portfolios",
        404: "User not found",
        500: "Could not update portfolio"
    })
    @api.doc(security='apiKey')
    @token_required
    def put(current_user) -> response:
        portfolio_name = get_request_parameter(name='portfolio_name', required=False, expected_type=str)

        portfolio_id, msg = get_request_parameter(name='portfolio_id', required=True, expected_type=str)
        if not portfolio_id:
            return response_400(msg)

        allocations, msg = get_request_parameter(name='allocations', required=True, expected_type=list)
        if not allocations:
            return response_400(msg)

        return response(*PortfolioManagementAPI.update_portfolio(user_id=current_user.public_id,
                                                                 portfolio_id=portfolio_id,
                                                                 new_allocations=allocations,
                                                                 portfolio_name=portfolio_name))

    @staticmethod
    @api.doc(params={
        "portfolio_id": api_param_query(required=True, description="Portfolio id")
    })
    @api.doc(responses={
        200: "OK",
        401: "Cannot delete other users\' portfolios",
        404: "Portfolio not found",
        500: "Could not delete portfolio"
    })
    @api.doc(security='apiKey')
    @token_required
    def delete(current_user) -> response:
        portfolio_id, msg = get_request_parameter(name="portfolio_id", expected_type=str, required=True)
        if not portfolio_id:
            return response_400(msg)
        return response(*PortfolioManagementAPI.delete_portfolio(user_id=current_user.public_id,
                                                                 portfolio_id=portfolio_id))


class RouteBacktest(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(params={
        "portfolio_id": api_param_query(required=True,
                                        description="Portfolio id"),
        "start_ts": api_param_query(required=False, description="Start timestamp", default=FIVE_YEARS_TS),
        "end_ts": api_param_query(required=False, description="End ts", default=int(time.time()))
    })
    @api.doc(responses={
        200: "OK",
        400: "Param <> is required.",
        401: 'Cannot backtest other users\' portfolios',
        404: "User not found. | Portfolio not found"
    })
    @api.doc(security='apiKey')
    @token_required
    def get(current_user) -> response:
        portfolio_id, msg = get_request_parameter(name="portfolio_id", expected_type=str, required=True)
        if not portfolio_id:
            return response_400(msg)

        start_ts = get_request_parameter('start_ts', required=False, expected_type=int)
        if not start_ts:
            start_ts = FIVE_YEARS_TS

        end_ts = get_request_parameter('end_ts', required=False, expected_type=int)
        if not end_ts:
            end_ts = int(time.time())

        return response(*PortfolioManagementAPI.backtest_portfolio(user_id=current_user.public_id,
                                                                   portfolio_id=portfolio_id,
                                                                   start_ts=start_ts,
                                                                   ends_ts=end_ts))
