from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI


class ESStockPrices:

    @staticmethod
    def get_ticker_first_date_price(ticker, start_ts):
        """
        Get first price of ticker starting from start_ts.
        @param ticker: string
        @param start_ts: int
        @return: dict {string: float}
        """

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        es_first_price_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
            'query': {'bool': {'must': [{'term': {'ticker': ticker.lower()}},
                                        {'range': {'date': {'gte': start_ts}}}]}},
            "sort": [
                {
                    "date": {
                        "order": "asc"
                    }
                }
            ]
        }, size=1)

        if not (es_first_price_doc and es_first_price_doc.get('hits', {}).get('hits', [])):
            return None

        first_price_info = es_first_price_doc["hits"]["hits"][0]['_source']
        return {first_price_info['date']: first_price_info['close']}

    @staticmethod
    def get_ticker_last_date_price(ticker, end_ts):
        """
        Get last price of ticker starting from start_ts.
        @param ticker: string
        @param end_ts: int
        @return: dict {string: float}
        """

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        es_last_price_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
            'query': {'bool': {'must': [{'term': {'ticker': ticker.lower()}},
                                        {'range': {'date': {'lte': end_ts}}}]}},
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        }, size=1)

        if not (es_last_price_doc and es_last_price_doc.get('hits', {}).get('hits', [])):
            return None

        last_price_info = es_last_price_doc["hits"]["hits"][0]['_source']
        return {last_price_info['date']: last_price_info['close']}
