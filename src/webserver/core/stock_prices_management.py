"""
Stock management APIs.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time
from datetime import datetime

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI

LAST_DAY = 24 * 3600
LAST_WEEK = 7 * LAST_DAY


class StockPricesManagementAPI:

    @staticmethod
    def get_price_history_for_ticker(ticker, start_ts=0, end_ts=int(time.time())) -> tuple:
        """
        Get stock price history since start_ts until end_ts for specified ticker.
        @param ticker: string
        @param start_ts: start timestamp
        @param end_ts: end timestamp
        @return: tuple
        """
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

        price_history = {}
        for es_price_doc in es_dbi.scroll_search_documents_generator(config.ES_INDEX_STOCK_PRICES, query_body={
            'query': {
                'bool': {
                    'must': [{'term': {'ticker': ticker.lower()}},
                             {'range': {'date': {'gte': start_ts, 'lte': end_ts}}}]
                }
            }
        }):
            date = datetime.fromtimestamp(es_price_doc['_source'].get('date', None)).strftime('%Y-%m-%d')
            price_history[date] = es_price_doc["_source"]

        if not price_history:
            return 404, {}, 'No price history for ticker {}'.format(ticker)

        price_history = {k: v for k, v in sorted(price_history.items(), key=lambda x: x[0], reverse=True)}
        return 200, price_history, 'OK'
