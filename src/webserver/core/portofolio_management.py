import time
from datetime import datetime

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from webserver.decorators import fails_safe_request
from webserver.model.user import User

FIVE_YEARS_TS = int(time.time()) - 5 * 365 * 24 * 3600


class PortofolioManagementAPI:

    @staticmethod
    def check_user_exists(user_id) -> bool:
        """
        Check if user with user_id exists in SQL db.
        @param user_id: string
        @return: boolean
        """
        user = User.query.filter_by(public_id=user_id).first()
        if not user:
            return False
        return True

    @staticmethod
    @fails_safe_request
    def get_portofolio(user_id, portofolio_id=None, **kwargs) -> tuple:
        """
        Get portofolio with portofolio_id for specified user. If portofolio id not specified, return all current user
         portofolios.
        @param user_id: string
        @param portofolio_id: strin
        @return: tuple
        """

        if 'test' not in kwargs and not PortofolioManagementAPI.check_user_exists(user_id):
            return 404, {}, 'User not found.'

        es_query = {'query': {'bool': {'must': [{'match': {'user_id': user_id}}]}}}
        if portofolio_id:
            es_query['query']['bool']['must'].append({'term': {'_id': portofolio_id}})

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        es_portofolio_documents = es_dbi.search_documents(config.ES_INDEX_PORTOFOLIOS, query_body=es_query)
        if es_portofolio_documents and es_portofolio_documents.get('hits', {}).get('hits', []):
            return 200, {portofolio['_id']: portofolio['_source'] for portofolio in
                         es_portofolio_documents['hits']['hits']}, 'OK'

        return 404, {}, 'Portofolio not found.'

    @staticmethod
    @fails_safe_request
    def create_portofolio(user_id, allocations, **kwargs) -> tuple:
        """
        Create portofolio for user.
        @param user_id: string
        @param allocations: list of dicts [{'ticker': <>, 'percentage': <>}]
        @param kwargs: dict
        @return: tuple
        """

        if 'test' not in kwargs and not PortofolioManagementAPI.check_user_exists(user_id):
            return 404, {}, 'User not found.'

        total_allocation = 0
        for allocation in allocations:
            if allocation.get('ticker', None) is None or allocation.get('percentage', None) is None:
                return 400, {}, 'Invalid allocation {}'.format(allocation)
            total_allocation += allocation["percentage"]

        if total_allocation != 100:
            return 400, {}, 'Total allocation percentage must be 100%.'

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_id = es_dbi.create_document(config.ES_INDEX_PORTOFOLIOS, document={
            'portofolio_name': kwargs.get('portofolio_name', 'user_portofolio_default'),
            'created_timestamp': int(time.time()),
            'modified_timestamp': int(time.time()),
            'user_id': user_id,
            'allocations': allocations})

        if portofolio_id:
            return 200, {'portofolio_id': portofolio_id}, 'OK'

        return 500, {}, 'Could not create portofolio.'

    @staticmethod
    @fails_safe_request
    def update_portofolio(user_id, portofolio_id, allocations, **kwargs) -> tuple:
        """
        Update user portofolio.
        @param user_id: string
        @param portofolio_id: string
        @param allocations: list of dicts [{'ticker': <>, 'percentage': <>}]
        @param kwargs: dict
        @return: tuple
        """

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_document = es_dbi.get_document_by_id(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id)
        if not portofolio_document:
            return 404, {}, 'Portofolio not found.'

        if portofolio_document["_source"]["user_id"] != user_id:
            return 401, {}, 'Cannot update other users\' portofolios'

        for allocation in allocations:
            if allocation.get('ticker', None) is None or allocation.get('percentage', None) is None:
                return 400, {}, 'Invalid allocation {}'.format(allocation)

        portofolio = portofolio_document['_source']
        portofolio['allocations'] = allocations
        portofolio['modified_timestamp']: int(time.time())
        if kwargs.get('portofolio_name', None):
            portofolio['portogolio_name'] = kwargs['portofolio_name']

        if es_dbi.update_document(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id, document=portofolio):
            return 200, {'portofolio_id': portofolio_id}, 'OK'

        return 500, {}, 'Could not update portofolio.'

    @staticmethod
    @fails_safe_request
    def delete_portofolio(user_id, portofolio_id) -> tuple:
        """
        Delete user portofolio.
        @param user_id: string
        @param portofolio_id: string
        @return: tuple
        """

        # check portofolio exists
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_document = es_dbi.get_document_by_id(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id)
        if not portofolio_document:
            return 404, {}, 'Portofolio not found.'

        if portofolio_document["_source"]["user_id"] != user_id:
            return 401, {}, 'Cannot delete other users\' portofolios'

        # delete
        if es_dbi.delete_document(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id):
            return 200, {}, 'OK'

        return 500, {}, 'Could not delete portofolio.'

    @staticmethod
    @fails_safe_request
    def backtest_portofolio(user_id, portofolio_id, start_ts=FIVE_YEARS_TS, ends_ts=int(time.time())) -> tuple:
        """
        Backtest user portofolio. Default interval 5 years ago - now.
        @param user_id: string
        @param portofolio_id: string
        @param start_ts: int
        @param ends_ts: int
        @return: tuple
        """

        # check portofolio exists
        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_document = es_dbi.get_document_by_id(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id)
        if not portofolio_document:
            return 404, {}, 'Portofolio not found.'

        # check portofolio owner
        if portofolio_document["_source"]["user_id"] != user_id:
            return 401, {}, 'Cannot backtest other users\' portofolios'

        # get allocations + prices
        allocations = portofolio_document['_source']['allocations']
        price_data = {'start_date': datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d'),
                      'end_date': datetime.fromtimestamp(ends_ts).strftime('%Y-%m-%d'),
                      'portofolio_data': {}}

        for ticker in {allocation['ticker'] for allocation in allocations}:
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
            es_first_price_doc = es_first_price_doc["hits"]["hits"][0]
            price_data['portofolio_data'][ticker] = {es_first_price_doc["_source"]["date"]: float(
                es_first_price_doc["_source"]["close"])}

            es_last_price_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
                'query': {'bool': {'must': [{'term': {'ticker': ticker.lower()}},
                                            {'range': {'date': {'lte': ends_ts}}}]}},
                "sort": [
                    {
                        "date": {
                            "order": "desc"
                        }
                    }
                ]
            }, size=1)
            es_last_price_doc = es_last_price_doc["hits"]["hits"][0]
            price_data['portofolio_data'][ticker][es_last_price_doc["_source"]["date"]] = float(
                es_last_price_doc["_source"]["close"])

        # compute return for each holding
        for ticker in price_data['portofolio_data']:
            start_ts, end_ts = min(list(price_data['portofolio_data'][ticker].keys())), max(
                list(price_data['portofolio_data'][ticker].keys()))

            price_data['portofolio_data'][ticker]['return_value_per_share'] = \
                price_data['portofolio_data'][ticker][end_ts] - price_data['portofolio_data'][ticker][start_ts]

            price_data['portofolio_data'][ticker]['return_percentage'] = \
                (100 * price_data['portofolio_data'][ticker][end_ts] / price_data['portofolio_data'][ticker][
                    start_ts]) - 100

        # compute total return
        price_data["total_return_percentage"] = round(sum(
            [allocation["percentage"] / 100 * price_data['portofolio_data'][allocation["ticker"]][
                "return_percentage"] for allocation in allocations]), 2)

        return 200, price_data, 'OK'
