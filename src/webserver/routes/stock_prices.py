"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time

from flask_restplus import Resource

from webserver.core.stock_prices_management import StockPricesManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.utils import api_param_query, api_param_form, get_request_parameter

api = FlaskRestPlusApi.get_instance()


class RouteStockPrices(Resource):

    @api.doc(params={
        "ticker": api_param_query(required=True,
                                  description="Company ticker"),
        "start": api_param_query(required=False,
                                 description="Time range start",
                                 enum=["LAST_DAY", "LAST_WEEK", "LAST_MONTH", "MTD", "LAST_YEAR", "YTD", "LAST_5_YEARS",
                                       "ALL"],
                                 default="LAST_WEEK"),
        "start_ts": api_param_query(required=False,
                                    description="Time range start timestamp",
                                    default=None),
        "end_ts": api_param_query(required=False,
                                  description="Time range end timestamp",
                                  default=int(time.time()))
    })
    @api.doc(responses={
        200: "OK",
        404: "No price history for ticker",
    })
    def get(self) -> response:
        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)

        start = get_request_parameter(name="start", expected_type=str, required=False) or "LAST_WEEK"
        start_ts = get_request_parameter(name="start_ts", expected_type=int, required=False)
        end_ts = get_request_parameter(name="end_ts", expected_type=int, required=False)

        return response(*StockPricesManagementAPI.get_price_history_for_ticker(ticker, start=start, start_ts=start_ts,
                                                                               end_ts=end_ts))

    @api.doc(params={
        "ticker": api_param_form(required=True,
                                 description="Company ticker")
    })
    @api.doc(responses={
        200: "OK",
        404: "No stock for ticker <> | No price history found for ticker <>."
    })
    def post(self) -> response:
        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)

        return response(*StockPricesManagementAPI.add_price_history_for_stock(ticker=ticker))

    @api.doc(params={
        "ticker": api_param_query(required=True,
                                  description="Company ticker")
    })
    @api.doc(responses={
        200: "OK",
        404: "No price history found for ticker <>. | Investment length must be greater or equal to 1",
    })
    def delete(self) -> response:
        ticker, msg = get_request_parameter(name="ticker", expected_type=str, required=True)
        if not ticker:
            return response_400(msg)

        return response(*StockPricesManagementAPI.delete_price_history_for_stock(ticker=ticker))