"""
Stock management APIs.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time
from datetime import datetime

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.utils import DEFAULT_LAST_PRICE_DATE, yf_get_historical_price_data_for_ticker, get_last_price_date_for_ticker
from webserver.core.consts import TIME_RANGES
from webserver.decorators import fails_safe_request


class StockPricesManagementAPI:

    @staticmethod
    @fails_safe_request
    def get_price_history_for_ticker(ticker, start_ts=TIME_RANGES["LAST_WEEK"], end_ts=int(time.time())) -> tuple:
        """
        Get stock price history since start until end for specified ticker.
        @param ticker: string
        @param start_ts: start as timestamp
        @param end_ts: end timestamp
        @return: tuple
        """
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        price_history = {}
        for es_price_doc in es_dbi.scroll_search_documents_generator(config.ES_INDEX_STOCK_PRICES, query_body={
            "query": {
                "bool": {
                    "must": [
                        {"term": {"ticker": ticker.lower()}},
                        {"range": {"date": {"gte": start_ts, "lte": end_ts}}}]
                }
            }
        }):
            if es_price_doc["_source"]["ticker"].lower() == ticker.lower():
                date = datetime.fromtimestamp(es_price_doc["_source"].get("date", None)).strftime("%Y-%m-%d")
                price_history[date] = es_price_doc["_source"]

        if not price_history:
            return 404, {}, "No price history for ticker {} for specified time range.".format(ticker)

        price_history = {k: v for k, v in sorted(price_history.items(), key=lambda x: x[0], reverse=True)}
        return 200, price_history, "OK"

    @staticmethod
    @fails_safe_request
    def add_price_history_for_stock(ticker) -> tuple:
        """
        Add historical prices for specified ticker.
        @param ticker: string
        @return: tuple
        """

        # connect to es
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        # check ticker in stocks index
        if not es_dbi.get_document_by_id(config.ES_INDEX_STOCKS, _id=ticker.upper()):
            return 404, {}, "No stock for ticker {}.".format(ticker)

        # get last known price date (if any)
        start_date = get_last_price_date_for_ticker(ticker=ticker, es_dbi=es_dbi)
        if not start_date:
            start_date = DEFAULT_LAST_PRICE_DATE

        # get historical prices
        prices = yf_get_historical_price_data_for_ticker(
            ticker=ticker,
            start_date=start_date,
            end_date=datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d"))

        if not prices:
            return 404, {}, "No price history found for ticker {}.".format(ticker)

        # index prices
        actions = []
        for price in prices:
            actions.append({"_index": config.ES_INDEX_STOCK_PRICES,
                            "_source": price})
            # do bulk insert
            if len(actions) >= 1000:
                es_dbi.bulk(actions, chunk_size=len(actions), max_retries=3)
                actions = []
        if actions:
            es_dbi.bulk(actions, chunk_size=len(actions), max_retries=3)

        es_dbi.refresh_index(config.ES_INDEX_STOCK_PRICES)

        return 200, prices, "OK"

    @staticmethod
    @fails_safe_request
    def delete_price_history_for_stock(ticker) -> tuple:
        """
        Delete price history for ticker from stock_prices index.
        @param ticker: string
        @return: tuple
        """

        # connect to es
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        # delete price history
        actions = []
        for es_price_history_document in es_dbi.scroll_search_documents_generator(
                config.ES_INDEX_STOCK_PRICES,
                query_body={
                    "query": {"bool": {"must": [{"term": {"ticker": ticker.lower()}}]}}
                }):
            if es_price_history_document["_source"]["ticker"].upper() == ticker:
                actions.append({"_index": config.ES_INDEX_STOCK_PRICES,
                                "_op_type": "delete",
                                "_id": es_price_history_document["_id"]})

        if not actions:
            return 404, False, "No price history found for ticker {}".format(ticker)

        while actions:
            batch = actions[:1000]
            es_dbi.bulk(actions=batch, chunk_size=len(batch))
            if len(actions) > 1000:
                actions = actions[1000:]
            else:
                actions = []

        es_dbi.refresh_index(config.ES_INDEX_STOCK_PRICES)

        return 200, True, "OK"
