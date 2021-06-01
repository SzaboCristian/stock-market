"""
Stock management APIs.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import calendar
import time
from datetime import datetime

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI

NOW_DATE = datetime.now()
NOW_TIMESTAMP = int(time.time())
ONE_DAY = 24 * 3600
ONE_WEEK = 7 * ONE_DAY
TIME_RANGES = {
    'LAST_DAY': NOW_TIMESTAMP - ONE_DAY,
    'LAST_WEEK': NOW_TIMESTAMP - ONE_WEEK,
    'LAST_MONTH': NOW_TIMESTAMP - calendar.monthrange(NOW_DATE.year, NOW_DATE.month)[1] * ONE_DAY,
    'MTD': NOW_TIMESTAMP - (NOW_DATE.day - 1) * ONE_DAY,
    'LAST_YEAR': NOW_TIMESTAMP - 365 * ONE_DAY,
    'YTD': NOW_TIMESTAMP - (NOW_DATE.timetuple().tm_yday - 1) * ONE_DAY,
    'LAST_5_YEARS': NOW_TIMESTAMP - 5 * 365 * ONE_DAY,
    'ALL': 0
}


class StockPricesManagementAPI:

    @staticmethod
    def get_price_history_for_ticker(ticker, start='LAST_WEEK', start_ts=None, end_ts=NOW_TIMESTAMP) -> tuple:
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
                return 400, {}, 'Invalid time range'
            start_ts = TIME_RANGES[start]

        for es_price_doc in es_dbi.scroll_search_documents_generator(config.ES_INDEX_STOCK_PRICES, query_body={
            'query': {
                'bool': {
                    'must': [
                        {"term": {"ticker": ticker.lower()}},
                        {'range': {'date': {'gte': start_ts, 'lte': end_ts}}}]
                }
            }
        }):
            if es_price_doc["_source"]["ticker"].lower() == ticker.lower():
                date = datetime.fromtimestamp(es_price_doc['_source'].get('date', None)).strftime('%Y-%m-%d')
                price_history[date] = es_price_doc["_source"]

        if not price_history:
            return 404, {}, 'No price history for ticker {} for specified time range.'.format(ticker)

        price_history = {k: v for k, v in sorted(price_history.items(), key=lambda x: x[0], reverse=True)}
        return 200, price_history, 'OK'
