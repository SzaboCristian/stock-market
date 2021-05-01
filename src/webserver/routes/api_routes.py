"""
API Route classes.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import json

from flask import request
from flask_restplus import Resource

from webserver.core.stock_prices_management import StockPricesManagementAPI
from webserver.core.stocks_management import StocksManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.utils import api_param_query, api_param_form

api = FlaskRestPlusApi.get_instance()


class RouteStocks(Resource):

    @api.doc(params={
        "ticker": api_param_query(required=False,
                                  description="Company ticker"),
        "sector": api_param_query(required=False,
                                  description="Sector"),
        "industry": api_param_query(required=False,
                                    description="Industry"),
        "tags": api_param_query(required=False,
                                description="Tags"),
        "tickers_only": api_param_query(required=False,
                                        description="Only return tickers",
                                        default=False,
                                        enum=[True, False])
    })
    @api.doc(responses={
        200: "OK",
        404: "No stocks found for specified filter."
    })
    def get(self) -> response:
        ticker = request.args.get("ticker", None)
        sector = request.args.get("sector", None)
        industry = request.args.get("industry", None)
        tags = request.args.get("tags", None)
        tickers_only = request.args.get("tickers_only", False)
        if isinstance(tickers_only, str):
            tickers_only = json.loads(tickers_only.lower())

        return response(*StocksManagementAPI.get_stocks(ticker=ticker, sector=sector, industry=industry,
                                                        tags=tags, ticker_only=tickers_only))

    @api.doc(params={
        "ticker": api_param_form(required=True, description="Company ticker"),
    })
    @api.doc(responses={
        200: "OK",
        201: "OK",
        400: "No ticker provided.",
        500: "Could not save info for ticker <>."
    })
    def post(self) -> response:
        ticker = request.form.get("ticker", None)
        if not ticker:
            return response_400("No ticker provided")
        return response(*StocksManagementAPI.add_stock(ticker=ticker))


class RouteStockPrices(Resource):

    @api.doc(params={
        "ticker": api_param_query(required=True,
                                  description="Company ticker"),
    })
    @api.doc(responses={
        200: "OK",
        404: "No price history for ticker",
    })
    def get(self) -> response:
        ticker = request.args.get("ticker", None)
        if not ticker:
            return 400, {}, 'Param ticker is required'

        # TODO add start_ts, end_ts date picker
        return response(*StockPricesManagementAPI.get_price_history_for_ticker(ticker))
