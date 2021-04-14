"""
Stock management APIs.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from yfinance import Ticker

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.logger.logger import Logger

EXCHANGE_NAMES = {"NMS": "National Market System",
                  "BTS": "BitShares BTS",
                  "NGM": "Nordic Growth Market",
                  "PCX": "Pacific Exchange",
                  "PNK": "Pink Sheets (OTC)",
                  "NYQ": "New York Stock Exchange",
                  "NCM": "NCM Nasdaq Commodities",
                  "ASE": "Amman Stock Exchange"
                  }


class StocksManagementAPI:

    #########
    # Utils #
    #########

    @staticmethod
    def get_exchange_name(exchange) -> str:
        """
        Return exchange full name.
        @param exchange: string, exchange abbreviation.
        @return: string
        """
        if exchange not in EXCHANGE_NAMES:
            return exchange
        return EXCHANGE_NAMES[exchange]

    @staticmethod
    def get_info_by_ticker(ticker) -> dict:
        """
        Get ticker info using yfinance and format result.
        @param ticker: string
        @return: dict
        """
        yf_ticker = Ticker(ticker)
        try:
            _ = yf_ticker.info
        except Exception as e:
            Logger.exception("No info for ticker {}. {}".format(ticker, str(e)))
            return {}

        info = dict()
        info["ticker"] = ticker
        info["names"] = [yf_ticker.info.get("longName", None)]
        short_name = yf_ticker.info.get("shortName", None)
        if not info["names"] or (short_name and info["names"][0].lower() != short_name.lower()):
            info["names"].append(short_name.rstrip(" -"))

        info["description"] = yf_ticker.info.get("longBusinessSummary", None)
        info["industry"] = yf_ticker.info.get("industry", None)
        info["sector"] = yf_ticker.info.get("sector", None)
        info["exchanges"] = [yf_ticker.info.get("exchange", None)]
        if info["exchanges"]:
            info["exchanges"] = [StocksManagementAPI.get_exchange_name(ex) for ex in info["exchanges"]]
        info["website"] = yf_ticker.info.get("website", None)
        info["tags"] = []

        for key in info:
            if isinstance(info[key], list):
                info[key] = [el for el in info[key] if el]

        info["names"] = list(set(info["names"]))

        tags = []
        if info["industry"]:
            tags.append(info["industry"])
        if info["sector"]:
            tags.append(info["sector"])
        tags = list(set(tags))

        if tags:
            info["tags"] = tags

        return info

    ########
    # APIs #
    ########

    @staticmethod
    def get_stocks(ticker=None, ticker_only=False) -> tuple:
        """
        Get stock information.
        @param ticker: string [Optional]
        @param ticker_only: boolean [Optional]
        @return: tuple
        """

        # connect to es and setup query
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        es_query = {"_source": False} if ticker_only else {}
        es_query["query"] = {
            "bool": {
                "must": [{
                    "term": {"_id": ticker}
                }]
            }
        } if ticker else {"match_all": {}}

        # search
        try:
            es_stocks = es_dbi.search_documents(config.ES_INDEX_STOCKS, query_body=es_query)
            if es_stocks["hits"]["total"]:
                es_stocks = es_stocks["hits"]["hits"]
                es_stocks = [es_stock["_id"] for es_stock in es_stocks] if ticker_only else {
                    es_stock["_id"]: es_stock["_source"] for es_stock in es_stocks}
        except Exception as e:
            Logger.exception(str(e))
            return 500, [], "Could not get stocks data."

        if not es_stocks:
            return 404, [], "No stocks found."

        return 200, es_stocks, "OK"

    @staticmethod
    def add_stock(ticker) -> tuple:
        """
        Get ticker info and index to Elasticsearch stocks index. Flask server daemon stock_prices_daemon will index
        price history for stock to stock_prices index.
        @param ticker: string
        @return: tuple
        """

        # check if ticker already in Elasticsearch
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        ticker_document = es_dbi.get_document_by_id(config.ES_INDEX_STOCKS, _id=ticker)
        if ticker_document:
            return 200, ticker_document["_source"], "OK"

        # Get ticker info
        ticker_info = StocksManagementAPI.get_info_by_ticker(ticker)
        if not ticker_info:
            return 400, {}, "Could not get info for ticker {}".format(ticker)

        # Save ticker info
        stock_added = es_dbi.create_document(config.ES_INDEX_STOCKS, _id=ticker_info["ticker"],
                                             document={k: v for k, v in ticker_info.items() if k != "ticker"})
        if stock_added:
            return 201, ticker_info, "OK"

        return 500, {}, "Could not save info for ticker {}".format(ticker)
