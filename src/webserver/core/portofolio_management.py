import time

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from webserver.decorators import fails_safe_request
from webserver.model.portofolio import Portofolio, PortofolioException, AllocationException, Allocation
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
        portofolios. No need for portofolio validation as they were alreay validated on creation/update.
        @param user_id: string
        @param portofolio_id: string
        @param kwargs: dict
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

        # porotofolio validation
        allocation_objects = []
        for allocation in allocations:
            try:
                allocation_objects.append(Allocation(allocation_json=allocation))
            except AllocationException:
                return 400, "Invalid allocation {}".format(allocation)

        try:
            portofolio = Portofolio(portofolio_json={
                'portofolio_name': kwargs.get('portofolio_name', 'user_portofolio_default'),
                'created_timestamp': int(time.time()),
                'modified_timestamp': int(time.time()),
                'user_id': user_id,
                'allocations': allocation_objects})
        except PortofolioException as e:
            return 400, {}, str(e)

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_id = es_dbi.create_document(config.ES_INDEX_PORTOFOLIOS, document=portofolio.get_data())

        if portofolio_id:
            return 200, {'portofolio_id': portofolio_id}, 'OK'

        return 500, {}, 'Could not create portofolio.'

    @staticmethod
    @fails_safe_request
    def update_portofolio(user_id, portofolio_id, new_allocations, **kwargs) -> tuple:
        """
        Update user portofolio.
        @param user_id: string
        @param portofolio_id: string
        @param new_allocations: list of dicts [{'ticker': <>, 'percentage': <>}]
        @param kwargs: dict
        @return: tuple
        """

        es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        portofolio_document = es_dbi.get_document_by_id(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id)
        if not portofolio_document:
            return 404, {}, 'Portofolio not found.'

        if portofolio_document["_source"]["user_id"] != user_id:
            return 401, {}, 'Cannot update other users\' portofolios'

        # updated data validation
        new_allocation_objects = []
        for new_allocation in new_allocations:
            try:
                new_allocation_objects.append(Allocation(allocation_json=new_allocation))
            except AllocationException:
                return 400, "Invalid allocation {}".format(new_allocation)

        # updated portofolio validation + validation
        try:
            portofolio = Portofolio(portofolio_json={
                'portofolio_name': portofolio_document["_source"].get("portofolio_name", None),
                'created_timestamp': portofolio_document["_source"].get("created_timestamp", None),
                'modified_timestamp': portofolio_document["_source"].get("modified_timestamp", None),
                'user_id': portofolio_document["_source"].get("user_id", None),
                'allocations': new_allocation_objects})
        except PortofolioException as e:
            return 400, {}, str(e)

        portofolio.set_modified_timestamp(int(time.time()))
        if kwargs.get('portofolio_name', None):
            portofolio.set_portofolio_name(kwargs['portofolio_name'])

        if es_dbi.update_document(config.ES_INDEX_PORTOFOLIOS, _id=portofolio_id, document=portofolio.get_data()):
            return 200, {'portofolio_id': portofolio_id}, 'OK'

        return 500, {}, 'Could not update portofolio.'

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

        # setup alloation objects
        allocation_objects = []
        for allocation in portofolio_document['_source']['allocations']:
            try:
                allocation_objects.append(Allocation(allocation_json=allocation))
            except AllocationException:
                return 400, "Invalid allocation {}".format(allocation)

        # setup portofolio object
        try:
            portofolio = Portofolio(portofolio_json={
                'portofolio_name': portofolio_document["_source"].get("portofolio_name", None),
                'created_timestamp': portofolio_document["_source"].get("created_timestamp", None),
                'modified_timestamp': portofolio_document["_source"].get("modified_timestamp", None),
                'user_id': portofolio_document["_source"].get("user_id", None),
                'allocations': allocation_objects})
        except PortofolioException as e:
            return 400, {}, str(e)

        return 200, portofolio.backtest(es_dbi=es_dbi, start_ts=start_ts, end_ts=ends_ts), 'OK'

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
