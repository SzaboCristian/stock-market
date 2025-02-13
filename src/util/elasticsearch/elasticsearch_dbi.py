"""
Elasticsearch Database Interface class.
"""

import logging
import time

from elasticsearch import (
    ConflictError,
    Elasticsearch,
    ElasticsearchException,
    NotFoundError,
    helpers,
)

from util.logger.logger import Logger

CONNECTION_TRIALS = 3
CONNECTION_TIMEOUT = 5


class ElasticsearchDBI:
    """
    Singleton class.
    """

    instance = None
    connected = False

    def __init__(self, host, port):
        """
        Singleton class constructor. Must not be called directly.
        @param host: string, elasticsearch host
        @param port: int, elasticsearch port
        """
        if ElasticsearchDBI.instance:
            raise ElasticsearchException(
                "Singleton Elasticsearch DBI called directly. Use ElasticsearchDBI.get_instance() method"
            )

        logging.info("Constructor - Elasticserch DBI @ {0}:{1}".format(host, port))

        try:
            self.__es = Elasticsearch(
                [{"host": host, "port": port}],
                timeout=60,
                retry_on_timeout=True,
                max_retries=10,
            )
            self.__host = host
            self.__port = port
            ElasticsearchDBI.connected = True
        except Exception as exception:
            logging.error(
                "Could not connect to ElasticSearch at {0}:{1}. Error was {2}".format(
                    host, port, str(exception)
                )
            )

        self.__tracer = logging.getLogger("elasticsearch")
        self.__tracer.setLevel(logging.INFO)
        self.__tracer.addHandler(logging.FileHandler("elasticsearch.log"))

    @staticmethod
    def get_instance(host, port):
        """
        Returns existing api_instance of ElasticsearchDBI class, or creates new api_instance if none exists.
        @param host: string
        @param port: string
        @return: ElasticsearchDBI object
        """
        if ElasticsearchDBI.instance is None:
            for _ in range(CONNECTION_TRIALS):
                ElasticsearchDBI.instance = ElasticsearchDBI(host=host, port=port)
                if ElasticsearchDBI.connected:
                    break
                Logger.error(
                    "Could not connect to Elasticsearch @ {0}:{1}".format(host, port)
                )
                ElasticsearchDBI.instance = None
                time.sleep(CONNECTION_TIMEOUT)

            if not ElasticsearchDBI.connected:
                raise ElasticsearchException(
                    "Could not connect to Elasticsearch @ {0}:{1} after {2} trials".format(
                        host, port, CONNECTION_TRIALS
                    )
                )

        return ElasticsearchDBI.instance

    ####################
    # INDEX MANAGEMENT #
    ####################

    def get_indices(self, alias="*") -> dict:
        """
        @param alias: string, alias/index name to match, default * (all)
        @return: dict
        """
        return self.__es.indices.get_alias(index=alias)

    def index_exists(self, index) -> bool:
        """
        @param index: string
        @return: boolean
        """
        return self.__es.indices.exists(index=index)

    def create_index(self, index, mappings=None) -> bool:
        """
        @param index: string
        @param mappings: dict
        @return: boolean
        """
        if self.index_exists(index):
            Logger.warning("Index {0} already exists".format(index))
            return False

        self.__es.indices.create(index=index, body=mappings)
        return True

    def refresh_index(self, index) -> bool:
        """
        @param index: string
        @return: boolean
        """
        if not self.index_exists(index):
            Logger.warning("Index {0} does not exist".format(index))
            return False

        self.__es.indices.refresh(index=[index])
        return True

    def delete_index(self, index) -> bool:
        """
        @param index: string
        @return: boolean
        """
        if not self.index_exists(index):
            Logger.warning("Index {0} does not exist".format(index))
            return False

        self.__es.indices.delete(index=index)
        return True

    def add_index_settings(self, index, settings) -> None:
        """
        @param index: string
        @param settings: dict
        @return: None
        """
        self.__es.indices.put_settings(index=index, body=settings)

    def put_mapping(self, index, mapping) -> None:
        """
        @param index: string
        @param mapping: dict
        @return: None
        """
        try:
            self.__es.indices.put_mapping(body=mapping, index=index)
        except Exception as exception:
            Logger.error(f"Error putting mapping for {index}: {exception}")

    ########################
    # DOCUMENTS MANAGEMENT #
    ########################

    def create_document(self, index, document, _id=None, refresh=True) -> object:
        """
        Create new document/overwrite existing.
        @param index: string
        @param document: dict
        @param _id: string/int
        @param refresh: boolean
        @return: _id: string/int/None - id of created document
        """
        try:
            inserted = self.__es.index(
                index=index, body=document, id=_id, refresh=refresh
            )
            return inserted["_id"]
        except ElasticsearchException as es_exception:
            Logger.error(es_exception)
            return None
        except Exception as exception:
            Logger.error(exception)
            return None

    def update_document(
        self, index, document, _id, mode="doc", refresh=True, retry_on_conflict=1
    ) -> bool:
        """
        Update document. Update is partial, i.e only specified fields are updated.
        @param index: string
        @param document: dict
        @param _id: string/int
        @param mode: string
        @param refresh: boolean
        @param retry_on_conflict: int
        @return: boolean
        """
        try:
            if mode not in ["doc", "script"]:
                raise Exception("Invalid update mode.")

            self.__es.update(
                index=index,
                body={mode: document},
                id=_id,
                refresh=refresh,
                retry_on_conflict=retry_on_conflict,
            )
            return True
        except (NotFoundError, ConflictError) as exception:
            Logger.error(
                "Could not update document {0}. Error was {1}".format(
                    _id, str(exception)
                )
            )
            return False

    def delete_document(self, index, _id, refresh=True) -> bool:
        """
        Delete document by id.
        @param index: string
        @param _id: string/int
        @param refresh: boolean
        @return: boolean
        """
        try:
            self.__es.delete(index, _id, refresh=refresh)
            return True
        except NotFoundError:
            return False

    def get_document_by_id(self, index, _id) -> object:
        """
        Get document by _id.
        @param index: string
        @param _id: string/int
        @return: dict/None
        """
        try:
            result = self.__es.get(index=index, id=_id)
            if "found" not in result or not result["found"]:
                return None
            return result
        except NotFoundError:
            return None

    def mget_documents_by_id(self, index, ids, _source_includes=None) -> object:
        """
        Get documents by ids batch.
        @param index: string
        @param ids: list
        @param _source_includes: list
        @return: dict/None
        """
        try:
            return self.__es.mget(
                body={"ids": ids}, index=index, _source_includes=_source_includes
            ).get("docs", [])
        except Exception as exception:
            Logger.error(exception)
            return None

    # SEARCH
    def search_documents(
        self, index="_all", query_body=None, size=10000, explain=False
    ) -> object:
        """
        Search documents that match the given query_body.
        @param index: string
        @param query_body: dict
        @param size: int
        @param explain: boolean
        @return: list/None
        """
        if not query_body:
            query_body = {"query": {"match_all": {}}}

        try:
            return self.__es.search(
                index=index, body=query_body, size=size, explain=explain
            )
        except Exception as exception:
            Logger.error("Search failed. {}".format(str(exception)))
            return None

    def scroll_search_documents_generator(
        self,
        index,
        query_body=None,
        size=10000,
        sort=None,
        scroll="60m",
        raise_on_error=False,
    ) -> object:
        """
        Scroll index and return documents that match query_body one by one (generator).
        @param index: string
        @param query_body: dict
        @param size: int
        @param sort: list
        @param scroll: string
        @param raise_on_error: boolean
        @return: dict/None
        """
        if not query_body:
            query_body = {"query": {"match_all": {}}}
        if not sort:
            sort = []

        try:
            data = self.__es.search(
                index=index, body=query_body, size=size, scroll=scroll, sort=sort
            )
            scroll_id = data["_scroll_id"]
            scroll_size = len(data["hits"]["hits"])

            for item in data["hits"]["hits"]:
                yield item

            while scroll_size > 0:
                data = self.__es.scroll(scroll_id=scroll_id, scroll=scroll)
                for item in data["hits"]["hits"]:
                    yield item

                scroll_id = data["_scroll_id"]
                scroll_size = len(data["hits"]["hits"])

            self.__es.clear_scroll(scroll_id=scroll_id)

        except Exception as exception:
            Logger.error(exception)
            if raise_on_error:
                raise exception
            return None

    # BULK
    def bulk(
        self,
        actions,
        chunk_size=1000,
        raise_on_error=False,
        max_retries=0,
        request_timeout=100,
    ) -> tuple:
        """
        Bulk operations. Most frequent _op_types: index, update, delete.
        @param actions: list
        @param chunk_size: int
        @param raise_on_error: boolean
        @param max_retries: int
        @param request_timeout: int
        @return: tuple
        """

        try:
            return helpers.bulk(
                self.__es,
                actions,
                chunk_size=chunk_size,
                raise_on_error=raise_on_error,
                max_retries=max_retries,
                request_timeout=request_timeout,
            )
        except Exception as exception:
            Logger.error("Error during bulk index: {0}".format(str(exception)))
            return -1, exception
