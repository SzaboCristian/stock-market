"""
API Route classes.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import json

from flask import request
from flask_restplus import Resource

from util.logger.logger import Logger
from webserver.core.stocks_management import StocksManagementAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response

api = FlaskRestPlusApi.get_instance()


def api_param(_in, required=True, description=None, **kwargs) -> dict:
    param = {
        "in": _in,
        "required": required,
        "description": description
    }
    param.update(dict(**kwargs))
    return param


def api_param_path(required=True, description=None, **kwargs) -> dict:
    return api_param("path", required, description, **kwargs)


def api_param_query(required=True, description=None, **kwargs) -> dict:
    return api_param("query", required, description, **kwargs)


def api_param_form(required=True, description=None, **kwargs) -> dict:
    return api_param("formData", required, description, **kwargs)


def api_param_body(required=True, description=None, **kwargs) -> dict:
    return api_param("body", required, description, **kwargs)


class RouteStocks(Resource):

    @api.doc(params={
        "ticker": api_param_query(required=False,
                                  description="Company ticker: string"),
        "tickers_only": api_param_query(required=False,
                                        description="Only return tickers",
                                        default=False,
                                        enum=[True, False])
    })
    @api.doc(responses={
        200: "OK",
        404: "No stocks found.",
        500: "Could not get stocks data."
    })
    def get(self) -> response:
        ticker = request.args.get("ticker", None)
        tickers_only = request.args.get("tickers_only", False)
        if isinstance(tickers_only, str):
            try:
                tickers_only = json.loads(tickers_only.lower())
            except Exception as e:
                Logger.exception("Invalid tickers_only param. Setting to default (False)")
                tickers_only = False

        return response(*StocksManagementAPI.get_stocks(ticker=ticker, ticker_only=tickers_only))

    @api.doc(params={
        "ticker": api_param_query(required=True, description="Company ticker: string"),
    })
    @api.doc(responses={
        200: "OK",
        201: "OK",
        400: "No ticker provided.",
        500: "Could not save info for ticker <>."
    })
    def post(self) -> response:
        ticker = request.args.get("ticker", None)
        if not ticker:
            return response_400("No ticker provided")
        return response(*StocksManagementAPI.add_stock(ticker=ticker))
