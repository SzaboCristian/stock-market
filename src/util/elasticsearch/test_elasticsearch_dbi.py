"""
ElasticsearchDBI test case.
"""

import unittest

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI


class TestElasticsearchDBI(unittest.TestCase):
    """
    Unit test case for Elasticsearch Database Interface - ElasticsearchDBI class.
    """

    def setUp(self) -> None:
        """
        Create ElasticsearchDBI object + setup test index name.
        @return: None
        """
        self.es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
        self.test_index_name = 'test_index'

    def tearDown(self) -> None:
        """
        Delete test index.
        @return: None
        """
        if self.es_dbi.index_exists(self.test_index_name):
            self.es_dbi.delete_index(self.test_index_name)
        self.es_dbi = None

    def test_create_index(self) -> None:
        """
        Test create test index.
        @return: None
        """

        if self.es_dbi.index_exists(self.test_index_name):
            self.es_dbi.delete_index(self.test_index_name)
        self.assertTrue(self.es_dbi.create_index(self.test_index_name))

    def test_get_indices(self) -> None:
        """
        Test get dictionary with all index names.
        @return: None
        """

        indices = self.es_dbi.get_indices()
        self.assertTrue(indices)
        self.assertTrue(isinstance(indices, dict))

    def test_index_exists(self) -> None:
        """
        Test index existence check.
        @return: None
        """

        indices = self.es_dbi.get_indices()
        self.assertTrue(indices)

        existing_index = list(indices.keys())[0]
        self.assertTrue(self.es_dbi.index_exists(existing_index))

        self.assertFalse(self.es_dbi.index_exists('inexistent_index_name'))

    def test_delete_index(self) -> None:
        """
        Test delete index.
        @return: None
        """

        if not self.es_dbi.index_exists(self.test_index_name):
            self.es_dbi.create_index(self.test_index_name)
        self.assertTrue(self.es_dbi.delete_index(self.test_index_name))

    def test_add_index_settings(self) -> None:
        """
        Test add index settings -> refresh_interval 1 second.
        @return: None
        """

        settings = {
            "settings": {
                "refresh_interval": "1s"
            }
        }
        if not self.es_dbi.index_exists(self.test_index_name):
            self.es_dbi.create_index(self.test_index_name)

        self.es_dbi.add_index_settings(index=self.test_index_name, settings=settings)

    def test_put_mapping(self) -> None:
        """
        Test put index mapping. Mappings must be specified when index is created.
        @return: None
        """

        temp_test_index = 'test_index2'
        mapping = {
            "mappings": {
                "properties": {
                    "some_string": {
                        "type": "text"
                    },
                    "some_bool": {
                        "type": "boolean"
                    }
                }
            }
        }
        # create temp index
        self.es_dbi.create_index(temp_test_index)

        # put mapping
        self.es_dbi.put_mapping(index=temp_test_index, mapping=mapping)

        # insert valid document
        self.assertTrue(self.es_dbi.create_document(index=temp_test_index, _id=1, document={"some_string": "Hello",
                                                                                            "some_bool": True}))

        # try insert malformed document
        self.assertFalse(self.es_dbi.create_document(index=temp_test_index, _id=1, document={"some_string": 100,
                                                                                             "some_bool": "not_bool"}))
        # delete temp index
        self.es_dbi.delete_index(temp_test_index)

    def test_create_document(self) -> None:
        """
        Test create elasticsearch document in test index.
        @return: None
        """

        if not self.es_dbi.index_exists(self.test_index_name):
            self.es_dbi.create_index(self.test_index_name)
        document_id = self.es_dbi.create_document(index=self.test_index_name, _id='test_id', document={'test': 'value'})
        self.assertEqual(document_id, 'test_id')

    def test_get_by_id(self) -> None:
        """
        Test document retrieval by id.
        @return: None
        """

        document_id = self.es_dbi.create_document(index=self.test_index_name, _id='test_id', document={'test': 'value'})
        es_document = self.es_dbi.get_document_by_id(index=self.test_index_name, _id=document_id)
        self.assertTrue(es_document)
        self.assertEqual(es_document.get('_id', None), document_id)

    def test_update_document(self) -> None:
        """
        Test update document.
        @return: None
        """

        document_id = self.es_dbi.create_document(index=self.test_index_name, _id='test_id', document={'test': 'value'})
        updated = self.es_dbi.update_document(index=self.test_index_name, _id=document_id,
                                              document={'test': 'new_value'})
        self.assertTrue(updated)
        updated_document = self.es_dbi.get_document_by_id(index=self.test_index_name, _id=document_id)
        self.assertTrue(updated_document)
        self.assertEqual(updated_document.get('_source', {}).get('test', None), 'new_value')

    def test_delete_document(self) -> None:
        """
        Test delete document.
        @return: None
        """

        document_id = self.es_dbi.create_document(index=self.test_index_name, _id='test_id', document={'test': 'value'})
        self.assertTrue(document_id)
        deleted = self.es_dbi.delete_document(index=self.test_index_name, _id=document_id)
        self.assertTrue(deleted)
        deleted_document = self.es_dbi.get_document_by_id(index=self.test_index_name, _id=document_id)
        self.assertFalse(deleted_document)

    def test_mget_by_id(self) -> None:
        """
        Test mget documents by ids batch.
        @return: None
        """

        document_id_1 = self.es_dbi.create_document(index=self.test_index_name, _id='test_id',
                                                    document={'test': 'value'})
        document_id_2 = self.es_dbi.create_document(index=self.test_index_name, _id='test_id2',
                                                    document={'test': 'value2'})
        documents = self.es_dbi.mget_documents_by_id(index=self.test_index_name, ids=[document_id_1, document_id_2])
        self.assertTrue(documents)
        for document in documents:
            self.assertTrue(document['found'])

    def test_search_documents(self) -> None:
        """
        Test documents search.
        @return: None
        """

        self.assertTrue(self.es_dbi.create_document(index=self.test_index_name,
                                                    _id='test_id',
                                                    document={'score': 100},
                                                    refresh=True))
        self.assertTrue(self.es_dbi.create_document(index=self.test_index_name,
                                                    _id='test_id2',
                                                    document={'score': 50},
                                                    refresh=True))

        # existing document
        searched_documents = self.es_dbi.search_documents(index=self.test_index_name, query_body={
            'query': {'bool': {'must': [{'term': {'score': 100}}]}}
        })
        self.assertTrue(searched_documents)
        self.assertTrue(searched_documents['hits']['hits'])
        for searched_document in searched_documents['hits']['hits']:
            self.assertEqual(searched_document['_source']['score'], 100)

        # non-existing document
        searched_documents = self.es_dbi.search_documents(index=self.test_index_name, query_body={
            'query': {'bool': {'must': [{'term': {'score': 75}}]}}
        })
        self.assertTrue(searched_documents)
        self.assertFalse(searched_documents['hits']['hits'])

    def test_scroll_search_documents(self) -> None:
        """
        Test scroll search using generator.
        @return: None
        """

        at_least_one_doc = False
        self.assertTrue(self.es_dbi.create_document(index=self.test_index_name,
                                                    _id='test_id',
                                                    document={'test': 'value'},
                                                    refresh=True))
        for es_doc in self.es_dbi.scroll_search_documents_generator(index=self.test_index_name):
            at_least_one_doc = True
            self.assertTrue(es_doc)
            self.assertTrue(es_doc['_id'])
            self.assertTrue(es_doc['_source'])
        self.assertTrue(at_least_one_doc)

    def test_bulk(self) -> None:
        """
        Test bulk operations: insert, update, delete.
        @return: None
        """

        # bulk insert
        actions = [
            {'_index': self.test_index_name,
             '_id': 'document_id_1',
             '_source': {'test': 'value'}},
            {'_index': self.test_index_name,
             '_id': 'document_id_2',
             '_source': {'test': 'value'}},
        ]
        success, failed = self.es_dbi.bulk(actions=actions, chunk_size=len(actions))
        self.assertEqual(success, 2)
        self.assertFalse(failed)

        # bulk update
        actions = [
            {'_op_type': 'update',
             '_index': self.test_index_name,
             '_id': 'document_id_1',
             'doc': {'test': 'value2'}},
            {'_op_type': 'update',
             '_index': self.test_index_name,
             '_id': 'document_id_2',
             'doc': {'test': 'value3'}},
        ]
        success, failed = self.es_dbi.bulk(actions=actions, chunk_size=len(actions))
        self.assertEqual(success, 2)
        self.assertFalse(failed)

        # bulk delete
        actions = [
            {'_op_type': 'delete',
             '_index': self.test_index_name,
             '_id': 'document_id_1'},
            {'_op_type': 'delete',
             '_index': self.test_index_name,
             '_id': 'document_id_2'},
        ]
        success, failed = self.es_dbi.bulk(actions=actions, chunk_size=len(actions))
        self.assertEqual(success, 2)
        self.assertFalse(failed)


if __name__ == '__main__':
    unittest.main()
