"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from flask_restplus import Resource

from webserver import decorators
from webserver.core.stocks_management import StocksManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.authentication import token_required
from webserver.routes.utils import api_param_query, api_param_form, get_request_parameter

api = FlaskRestPlusApi.get_instance()


class RouteStocks(Resource):
    method_decorators = [decorators.webserver_logger]


    @staticmethod
    @api.doc(params={
        "ticker": api_param_query(required=False,
                                  description="Company ticker"),
        "company_name": api_param_query(required=False,
                                        description="Company name"),
        "sector": api_param_query(required=False,
                                  description="Sector"),
        "industry": api_param_query(required=False,
                                    description="Industry"),
        "tags": api_param_query(required=False,
                                description="Tags"),
        "exchange": api_param_query(required=False,
                                    description="Stock Exchange"),
        "legal_type": api_param_query(required=False,
                                      description="Legal type"),
        "tickers_only": api_param_query(required=False,
                                        description="Only return tickers",
                                        default=False,
                                        enum=[True, False])
    })
    @api.doc(responses={
        200: "OK",
        404: "No stocks found for specified filter."
    })
    def get() -> response:
        ticker = get_request_parameter(name="ticker", expected_type=str, required=False)
        company_name = get_request_parameter(name="company_name", expected_type=str, required=False)
        sector = get_request_parameter(name="sector", expected_type=str, required=False)
        industry = get_request_parameter(name="industry", expected_type=str, required=False)
        tags = get_request_parameter(name="tags", expected_type=str, required=False)
        exchange = get_request_parameter(name="exchange", expected_type=str, required=False)
        legal_type = get_request_parameter(name="legal_type", expected_type=str, required=False)
        tickers_only = get_request_parameter(name="tickers_only", expected_type=bool, required=False)

        return response(*StocksManagementAPI.get_stocks(ticker=ticker, company_name=company_name, sector=sector,
                                                        industry=industry, tags=tags, exchange=exchange,
                                                        legal_type=legal_type, ticker_only=tickers_only))

    @staticmethod
    @api.doc(params={
        "ticker": api_param_form(required=True, description="Company ticker"),
    })
    @api.doc(responses={
        200: "OK",
        201: "OK",
        400: "No ticker provided.",
        500: "Could not save info for ticker <>."
    })
    @api.doc(security='apiKey')
    @token_required
    def post(current_user) -> response:
        if not current_user.admin:
            return response(401, {}, 'Unauthorized operation.')

        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)
        return response(*StocksManagementAPI.add_stock(ticker=ticker))

    @staticmethod
    @api.doc(params={
        "ticker": api_param_form(required=True, description="Company ticker"),
        "ticker_info": api_param_form(required=True, description="Updated information (json dict)")
    })
    @api.doc(responses={
        200: "OK",
        400: "No ticker provided. | No update info provided.",
        500: "Could not update info for ticker <>."
    })
    @api.doc(security='apiKey')
    @token_required
    def put(current_user) -> response:
        if not current_user.admin:
            return response(401, {}, 'Unauthorized operation.')

        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)

        ticker_info, msg = get_request_parameter(name="ticker_info", expected_type=dict, required=True)
        if not ticker_info:
            return response_400(msg)

        return response(*StocksManagementAPI.update_stock_info(ticker=ticker, updated_info=ticker_info))

    @staticmethod
    @api.doc(params={
        "ticker": api_param_query(required=True,
                                  description="Company ticker")
    })
    @api.doc(responses={
        200: "OK",
        404: "Ticker <> not found.",
    })
    @api.doc(security='apiKey')
    @token_required
    def delete(current_user) -> response:
        if not current_user.admin:
            return response(401, {}, 'Unauthorized operation.')
        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)

        return response(*StocksManagementAPI.delete_stock(ticker=ticker))
