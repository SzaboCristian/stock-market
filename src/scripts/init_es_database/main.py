"""
Script initializes ES indices. Mappings are specified in es_mappings.py file.
"""
__version__ = '0.0.1'
__author__ = 'Szabo Cristian'

from scripts.init_es_database.es_mappings import ES_INDEX_STOCKS_MAPPINGS, ES_INDEX_STOCK_PRICES_MAPPINGS, \
    ES_INDEX_PORTOFOLIOS_MAPPINGS
from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.logger.logger import Logger

INDEX_MAPPINGS = {config.ES_INDEX_STOCKS: ES_INDEX_STOCKS_MAPPINGS,
                  config.ES_INDEX_STOCK_PRICES: ES_INDEX_STOCK_PRICES_MAPPINGS,
                  config.ES_INDEX_PORTOFOLIOS: ES_INDEX_PORTOFOLIOS_MAPPINGS}


def create_indices(recreate=False):
    """
    Create ES indices and put their mappings.
    @return: boolean
    """
    es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

    if recreate:
        for name in INDEX_MAPPINGS:
            es_dbi.delete_index(name)

    for index_name in INDEX_MAPPINGS:
        if es_dbi.index_exists(index_name):
            Logger.info('Index {} already exists'.format(index_name))
            continue

        if not es_dbi.create_index(index_name, mappings=INDEX_MAPPINGS[index_name]):
            Logger.error('Could not create {} index'.format(index_name))
            return False

    return True


if __name__ == '__main__':
    create_indices(recreate=True)
