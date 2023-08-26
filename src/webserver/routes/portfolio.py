"""
API Route class.
"""

import time

from flask_restplus import Resource

from webserver import decorators
from webserver.core.consts import TIME_RANGES
from webserver.core.portfolio_management import PortfolioManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response, response_400
from webserver.routes.authentication import token_required
from webserver.routes.utils import (api_param_form, api_param_query,
                                    get_request_parameter)

api = FlaskRestPlusApi.get_instance()

FIVE_YEARS_TS = int(time.time()) - 5 * 365 * 24 * 3600


class RoutePortfolio(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(description="Get current user portfolios.")
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
    @api.doc(description="Create portfolio for current user.")
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
    @api.doc(description="Update current user portfolio.")
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
    @api.doc(description="Delete current user portfolio.")
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
    @api.doc(description="Backtest current user portfolio.")
    @api.doc(params={
        "portfolio_id": api_param_query(required=True,
                                        description="Portfolio id"),
        "start_ts": api_param_query(required=False, description="Start timestamp"),
        "start": api_param_query(required=False,
                                 description="Time range start",
                                 enum=["LAST_WEEK", "LAST_MONTH", "MTD", "LAST_YEAR", "YTD", "LAST_5_YEARS",
                                       "ALL"],
                                 default="LAST_5_YEARS"),
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
        start = get_request_parameter(name="start", expected_type=str, required=False) or "LAST_5_YEARS"
        if start_ts is None:
            if start not in TIME_RANGES:
                return response_400("Invalid time range")
            start_ts = TIME_RANGES[start]

        end_ts = get_request_parameter(name='end_ts', expected_type=int, required=False)
        if end_ts is None:
            end_ts = int(time.time())

        return response(*PortfolioManagementAPI.backtest_portfolio(user_id=current_user.public_id,
                                                                   portfolio_id=portfolio_id,
                                                                   start_ts=start_ts,
                                                                   ends_ts=end_ts))
