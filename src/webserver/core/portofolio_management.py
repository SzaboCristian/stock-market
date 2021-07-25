import logging
import time

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from webserver.models.user import User


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
    def get_portofolio(user_id, portofolio_id=None) -> tuple:
        """
        TODO
        @param user_id:
        @param portofolio_id:
        @return:
        """
        if not PortofolioManagementAPI.check_user_exists(user_id):
            return 400, {}, 'User not found.'

        es_query = {'query': {'bool': {'must': [{'match': {'user_id': user_id}}]}}}
        if portofolio_id:
            es_query['query']['bool']['must'].append({'term': {'_id': portofolio_id}})

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        es_portofolio_documents = es_dbi.search_documents(config.ES_INDEX_PORTOFOLIOS, query_body=es_query)
        if es_portofolio_documents and es_portofolio_documents.get('hits', {}).get('hits', []):
            return 200, es_portofolio_documents['hits']['hits'], 'OK'

        return 404, {}, 'Portofolio not found.'

    @staticmethod
    def create_portofolio(user_id, allocations, **kwargs) -> tuple:
        """
        TODO
        @param user_id:
        @param allocations:
        @param kwargs:
        @return:
        """
        if not PortofolioManagementAPI.check_user_exists(user_id):
            return 400, {}, 'User not found.'

        for allocation in allocations:
            if allocation.get('ticker', None) is None or allocation.get('percentage', None) is None:
                return 400, {}, 'Invalid allocation {}'.format(allocation)
            # TODO - check each ticker exists in db
            # TODO check total percentage = 100

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
    def update_portofolio(user_id, portofolio_id, allocations, **kwargs) -> tuple:
        """
        TODO
        @param user_id:
        @param portofolio_id:
        @param allocations:
        @param kwargs:
        @return:
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
            return 200, {'message': 'Portofolio {} updated'.format(portofolio_id)}, 'OK'

        return 500, {}, 'Could not update portofolio.'

    @staticmethod
    def delete_portofolio(user_id, portofolio_id) -> tuple:
        """

        @param user_id:
        @param portofolio_id:
        @return:
        """

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_document = es_dbi.get_document_by_id(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id)
        if not portofolio_document:
            return 404, {}, 'Portofolio not found.'

        if portofolio_document["_source"]["user_id"] != user_id:
            return 401, {}, 'Cannot delete other users\' portofolios'

        if es_dbi.delete_document(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id):
            return 200, {}, 'OK'

        return 500, {}, 'Could not delete portofolio.'

    @staticmethod
    def backtest_portofolio(portofolio_id, start_ts, ends_ts) -> tuple:
        """
        TODO
        @param portofolio_id:
        @param start_ts:
        @param ends_ts:
        @return:
        """
        return 200, {}, 'OK'
