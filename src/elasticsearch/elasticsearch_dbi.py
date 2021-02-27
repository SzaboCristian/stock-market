import logging
import time

from elasticsearch import Elasticsearch

CONNECTION_TRIALS = 3
CONNECTION_TIMEOUT = 5


class ElasticsearchConnectionError(Exception):
    pass


class ElasticsearchDBI:
    # Singleton class

    instance = None
    connected = False

    def __init__(self, host, port):
        if ElasticsearchDBI.instance:
            raise ElasticsearchConnectionError(
                "Singleton Elasticsearch DBI called directly. Use ElasticsearchDBI.instance() method")

        logging.info("Constructor - Elasticserch DBI @ {0}:{1}".format(host, port))

        try:
            self.__es = Elasticsearch([{"host": host, "port": port}], timeout=60)
            self.__host = host
            self.__port = port
            ElasticsearchDBI.connected = True
        except Exception as e:
            logging.error("Could not connect to ElasticSearch at {0}:{1}. Error was {2}".format(host, port, str(e)))

        self.__tracer = logging.getLogger('elasticsearch')
        self.__tracer.setLevel(logging.INFO)
        self.__tracer.addHandler(logging.FileHandler('elasticsearch.log'))

    @staticmethod
    def instance(host, port):
        if ElasticsearchDBI.instance is None:
            for trial in range(CONNECTION_TRIALS):
                ElasticsearchDBI.instance = ElasticsearchDBI(host=host, port=port)
                logging.info('GOT INSTANCE {}'.format(ElasticsearchDBI.instance))
                if ElasticsearchDBI.connected:
                    break
                else:
                    logging.error('Could not connect to Elasticsearch @ {0}:{1}'.format(host, port))
                    ElasticsearchDBI.instance = None
                    time.sleep(CONNECTION_TIMEOUT)

            if not ElasticsearchDBI.connected:
                raise ElasticsearchConnectionError(
                    'Could not connect to Elasticsearch @ {0}:{1} after {2} trials'.format(host, port,
                                                                                           CONNECTION_TRIALS))

        return ElasticsearchDBI.instance

    # INDEX
    def get_indices(self):
        pass

    def index_exists(self):
        pass

    def create_index(self):
        pass

    def delete_index(self):
        pass

    def add_index_settings(self):
        pass

    # DOCUMENTS
    def create_document(self):
        pass

    def update_document(self):
        pass

    def delete_document(self):
        pass

    def get_document_by_id(self):
        pass

    def mget_documents_by_id(self):
        pass

    # SEARCH
    def search_documents(self):
        pass

    def scroll_search_documents(self):
        pass

    # BULK
    def bulk(self):
        pass

    # MAPPINGS
    def put_mappings(self):
        pass
