"""
Stock management APIs.
"""

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.utils import EXCHANGE_NAMES, yf_get_info_for_ticker
from webserver.decorators import fails_safe_request


class StocksManagementAPI:
    ########
    # APIs #
    ########

    @staticmethod
    @fails_safe_request
    def get_stocks(
        ticker=None,
        company_name=None,
        sector=None,
        industry=None,
        tags=None,
        exchange=None,
        legal_type=None,
        ticker_only=False,
    ) -> tuple:
        """
        Get stocks information.
        @param ticker: string
        @param company_name: string
        @param sector: string
        @param industry: string
        @param tags: string
        @param exchange: string
        @param legal_type: string
        @param ticker_only: bool
        @return: tuple
        """

        # setup es query
        es_query = (
            {"_source": False, "query": {"match_all": {}}}
            if ticker_only
            else {"query": {"match_all": {}}}
        )
        if any([ticker, company_name, sector, industry, tags, exchange, legal_type]):
            es_query["query"] = {"bool": {"must": []}}
            if ticker:
                es_query["query"]["bool"]["must"].append(
                    {"term": {"_id": ticker.upper()}}
                )
            if company_name:
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"names": company_name_token.lower()}}
                        for company_name_token in company_name.split(" ")
                    ]
                )
            if sector:
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"sector": sector_token.lower()}}
                        for sector_token in sector.split(" ")
                    ]
                )
            if industry:
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"industry": industry_token.lower()}}
                        for industry_token in industry.split(" ")
                    ]
                )
            if tags:
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"tags": tag_token.lower()}}
                        for tag_token in tags.split(" ")
                    ]
                )
            if exchange:
                if exchange.upper() in EXCHANGE_NAMES:
                    exchange = EXCHANGE_NAMES[exchange.upper()]
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"exchanges": exchange_token.lower()}}
                        for exchange_token in exchange.split(" ")
                    ]
                )
            if legal_type:
                if legal_type.lower() == "etf":
                    legal_type = "Exchange Traded Fund"
                es_query["query"]["bool"]["must"].extend(
                    [
                        {"term": {"legal_type": legal_type_token.lower()}}
                        for legal_type_token in legal_type.split(" ")
                    ]
                )

        # connect
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )

        # search
        search_results = es_dbi.search_documents(
            config.ES_INDEX_STOCKS, query_body=es_query
        )
        if not search_results:
            return 500, {}, "Could not get stocks info from db."

        if not search_results["hits"]["total"]["value"]:
            return 404, {}, "No stocks found for specified filter."

        # format result
        search_results = (
            {
                search_result["_id"]: search_result["_source"]
                for search_result in search_results["hits"]["hits"]
            }
            if not ticker_only
            else [
                search_result["_id"] for search_result in search_results["hits"]["hits"]
            ]
        )

        return 200, search_results, "OK"

    @staticmethod
    @fails_safe_request
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
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )
        ticker_document = es_dbi.get_document_by_id(config.ES_INDEX_STOCKS, _id=ticker)
        if ticker_document:
            return 200, ticker_document["_source"], "OK"

        # Get ticker info
        ticker_info = yf_get_info_for_ticker(ticker)
        if not ticker_info:
            return 400, {}, "Could not get info for ticker {}".format(ticker)

        # Save ticker info
        stock_added = es_dbi.create_document(
            config.ES_INDEX_STOCKS,
            _id=ticker_info["ticker"],
            document={k: v for k, v in ticker_info.items() if k != "ticker"},
        )
        if not stock_added:
            return 500, {}, "Could not save info for ticker {}".format(ticker)

        return 201, ticker_info, "OK"

    @staticmethod
    @fails_safe_request
    def update_stock_info(ticker, updated_info) -> tuple:
        """
        Update ticker info with given updated_info.
        @param ticker: string
        @param updated_info: dict
        @return: tuple
        """

        ticker = ticker.upper()
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )

        ticker_document = es_dbi.get_document_by_id(config.ES_INDEX_STOCKS, _id=ticker)
        if not ticker_document:
            return (
                404,
                {},
                "Ticker {} not in db. Please use POST API to insert new ticker.".format(
                    ticker
                ),
            )

        updated = es_dbi.update_document(
            config.ES_INDEX_STOCKS, _id=ticker, document=updated_info
        )
        if not updated:
            return 500, False, "Could not update info for ticker {}.".format(ticker)

        return 200, True, "OK"

    @staticmethod
    @fails_safe_request
    def delete_stock(ticker) -> tuple:
        """
        Delete stock and price history for specified ticker.
        @param ticker: string
        @return: tuple
        """

        ticker = ticker.upper()
        es_dbi = ElasticsearchDBI.get_instance(
            config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT
        )

        # delete stock
        ticker_deleted = es_dbi.delete_document(config.ES_INDEX_STOCKS, _id=ticker)
        if not ticker_deleted:
            return 404, False, "Ticker {} not found".format(ticker)

        return 200, True, "OK"
