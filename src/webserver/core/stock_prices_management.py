"""
Stock management APIs.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import calendar
import time
from datetime import datetime

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.utils import DEFAULT_LAST_PRICE_DATE, yf_get_historical_price_data_for_ticker, get_last_price_date_for_ticker
from webserver.decorators import fails_safe_request

NOW_DATE = datetime.now()
NOW_TIMESTAMP = int(time.time())
ONE_DAY = 24 * 3600
ONE_WEEK = 7 * ONE_DAY
TIME_RANGES = {
    "LAST_DAY": NOW_TIMESTAMP - ONE_DAY,
    "LAST_WEEK": NOW_TIMESTAMP - ONE_WEEK,
    "LAST_MONTH": NOW_TIMESTAMP - calendar.monthrange(NOW_DATE.year, NOW_DATE.month)[1] * ONE_DAY,
    "MTD": NOW_TIMESTAMP - (NOW_DATE.day - 1) * ONE_DAY,
    "LAST_YEAR": NOW_TIMESTAMP - 365 * ONE_DAY,
    "YTD": NOW_TIMESTAMP - (NOW_DATE.timetuple().tm_yday - 1) * ONE_DAY,
    "LAST_5_YEARS": NOW_TIMESTAMP - 5 * 365 * ONE_DAY,
    "ALL": 0
}


class StockPricesManagementAPI:

    @staticmethod
    @fails_safe_request
    def get_price_history_for_ticker(ticker, start="LAST_WEEK", start_ts=None, end_ts=NOW_TIMESTAMP) -> tuple:
        """
        Get stock price history since start until end for specified ticker.
        @param ticker: string
        @param start: string in TIME_RANGE
        @param start_ts: start as timestamp
        @param end_ts: end timestamp
        @return: tuple
        """
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        price_history = {}
        if not start_ts:
            if start not in TIME_RANGES:
                return 400, {}, "Invalid time range"
            start_ts = TIME_RANGES[start]

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

        return 200, True, "OK"
