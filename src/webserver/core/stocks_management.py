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
    def get_stocks(ticker=None, sector=None, industry=None, tags=None, exchange=None, ticker_only=False) -> tuple:
        """
        Get stocks information.
        @param ticker: string
        @param sector: string
        @param industry: string
        @param tags: string
        @param exchange: string
        @param ticker_only: bool
        @return: tuple
        """

        # setup es query
        es_query = {"_source": False} if ticker_only else {}
        if not any([ticker, sector, industry, tags, exchange]):
            es_query["query"] = {"match_all": {}}
        else:
            es_query["query"] = {"bool": {"must": []}}
            if ticker:
                es_query["query"]["bool"]["must"].append({"term": {"_id": ticker.upper()}})
            if sector:
                es_query["query"]["bool"]["must"].extend(
                    [{"term": {"sector": sector_token.lower()}} for sector_token in sector.split(" ")])
            if industry:
                es_query["query"]["bool"]["must"].extend(
                    [{"term": {"industry": industry_token.lower()}} for industry_token in industry.split(" ")])
            if tags:
                es_query["query"]["bool"]["must"].extend(
                    [{"term": {"tags": tag_token.lower()}} for tag_token in tags.split(" ")])
            if exchange:
                if exchange.upper() in EXCHANGE_NAMES:
                    exchange = EXCHANGE_NAMES[exchange.upper()]
                es_query["query"]["bool"]["must"].extend(
                    [{"term": {"exchanges": exchange_token.lower()}} for exchange_token in exchange.split(" ")])

        # connect
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        # search
        search_results = es_dbi.search_documents(config.ES_INDEX_STOCKS, query_body=es_query)
        if not search_results:
            return 500, {}, "Could not get stocks info from db."

        if not search_results["hits"]["total"]["value"]:
            return 404, {}, "No stocks found for specified filter."

        # format result
        search_results = {
            search_result["_id"]: search_result["_source"] for search_result in
            search_results["hits"]["hits"]
        } if not ticker_only else \
            [search_result["_id"] for search_result in search_results["hits"]["hits"]]

        return 200, search_results, "OK"

    @staticmethod
    def add_stock(ticker) -> tuple:
        """
        Get ticker info and index to Elasticsearch stocks index. Flask server daemon stock_prices_daemon will index
        price history for stock to stock_prices index.
        @param ticker: string
        @return: tuple
        """

        # uppercase ticker
        ticker = ticker.upper()

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

    @staticmethod
    def update_stock_info(ticker, updated_info):
        """
        TODO
        @param ticker:
        @param updated_info:
        @return:
        """

        ticker = ticker.upper()
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        ticker_document = es_dbi.get_document_by_id(config.ES_INDEX_STOCKS, _id=ticker)
        if not ticker_document:
            return 404, {}, 'Ticker {} not in db. Please use POST API to insert new ticker.'.format(ticker)

        updated = es_dbi.update_document(config.ES_INDEX_STOCKS, _id=ticker, document=updated_info)
        if not updated:
            return 500, False, 'Could not update info for ticker {}.'.format(ticker)

        return 200, True, 'OK'
