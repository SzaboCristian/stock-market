import unittest

from elasticsearch.elasticsearch_dbi import ElasticsearchDBI

import config


class TestElasticsearchDBI(unittest.TestCase):
    def setUp(self) -> None:
        self.es = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

    def tearDown(self) -> None:
        self.es = None

    def test_get_indices(self):
        pass

    def test_index_exists(self):
        pass

    def test_create_index(self):
        pass

    def test_delete_index(self):
        pass

    def test_add_index_settings(self):
        pass

    def test_put_mapping(self):
        pass

    def test_create_document(self):
        pass

    def test_update_document(self):
        pass

    def test_delete_document(self):
        pass

    def test_get_by_id(self):
        pass

    def test_mget_by_id(self):
        pass

    def test_search_documents(self):
        pass

    def test_scroll_search_documents(self):
        pass

    def test_bulk(self):
        # bulk insert
        # bulk update
        # bulk delete
        pass
