"""
API Route class.
"""

import time

from flask_restplus import Resource

from webserver import decorators
from webserver.constants import TIME_RANGES
from webserver.core.stock_prices_management import StockPricesManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response, response_400
from webserver.routes.authentication import token_required
from webserver.routes.utils import (
    api_param_form,
    api_param_query,
    get_request_parameter,
)

api = FlaskRestPlusApi.get_instance()


class RouteStockPrices(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(description="Get stock price history")
    @api.doc(
        params={
            "ticker": api_param_query(required=True, description="Company ticker"),
            "start": api_param_query(
                required=False,
                description="Time range start",
                enum=[
                    "LAST_DAY",
                    "LAST_WEEK",
                    "LAST_MONTH",
                    "MTD",
                    "LAST_YEAR",
                    "YTD",
                    "LAST_5_YEARS",
                    "ALL",
                ],
                default="LAST_WEEK",
            ),
            "start_ts": api_param_query(
                required=False, description="Time range start timestamp", default=None
            ),
            "end_ts": api_param_query(
                required=False,
                description="Time range end timestamp",
                default=int(time.time()),
            ),
        }
    )
    @api.doc(
        responses={
            200: "OK",
            404: "No price history for ticker",
        }
    )
    def get() -> response:
        ticker, msg = get_request_parameter(
            name="ticker", expected_type=str, required=True
        )
        if not ticker:
            return response_400(msg)

        start_ts = get_request_parameter("start_ts", required=False, expected_type=int)
        start = (
            get_request_parameter(name="start", expected_type=str, required=False)
            or "LAST_WEEK"
        )
        if start_ts is None:
            if start not in TIME_RANGES:
                return response_400("Invalid time range")
            start_ts = TIME_RANGES[start]

        end_ts = get_request_parameter(name="end_ts", expected_type=int, required=False)

        return response(
            *StockPricesManagementAPI.get_price_history_for_ticker(
                ticker, start_ts=start_ts, end_ts=end_ts
            )
        )

    @staticmethod
    @api.doc(description="Add/update stock price history")
    @api.doc(
        params={"ticker": api_param_form(required=True, description="Company ticker")}
    )
    @api.doc(
        responses={
            200: "OK",
            404: "No stock for ticker <> | No price history found for ticker <>.",
        }
    )
    @api.doc(security="apiKey")
    @token_required
    def post(current_user) -> response:
        if not current_user.admin:
            return response(401, {}, "Unauthorized operation.")

        ticker, msg = get_request_parameter(
            name="ticker", expected_type=str, required=True
        )
        if not ticker:
            return response_400(msg)

        return response(
            *StockPricesManagementAPI.add_price_history_for_stock(ticker=ticker)
        )

    @staticmethod
    @api.doc(description="Delete stock price history")
    @api.doc(
        params={"ticker": api_param_query(required=True, description="Company ticker")}
    )
    @api.doc(
        responses={
            200: "OK",
            404: "No price history found for ticker <>. | Investment length must be greater or equal to 1",
        }
    )
    @api.doc(security="apiKey")
    @token_required
    def delete(current_user) -> response:
        if not current_user.admin:
            return response(401, {}, "Unauthorized operation.")

        ticker, msg = get_request_parameter(
            name="ticker", expected_type=str, required=True
        )
        if not ticker:
            return response_400(msg)

        return response(
            *StockPricesManagementAPI.delete_price_history_for_stock(ticker=ticker)
        )
