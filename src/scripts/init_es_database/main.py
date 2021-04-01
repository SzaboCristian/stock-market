import logging

import config
from scripts.init_es_database.es_mappings import ES_INDEX_STOCKS_MAPPINGS, ES_INDEX_STOCK_PRICES_MAPPINGS, \
    ES_INDEX_PORTOFOLIOS_MAPPINGS, ES_INDEX_USER_PORTOFOLIOS_MAPPINGS
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI

INDEX_MAPPINGS = {config.ES_INDEX_STOCKS: ES_INDEX_STOCKS_MAPPINGS,
                  config.ES_INDEX_STOCK_PRICES: ES_INDEX_STOCK_PRICES_MAPPINGS,
                  config.ES_INDEX_PORTOFOLIOS: ES_INDEX_PORTOFOLIOS_MAPPINGS,
                  config.ES_INDEX_USER_PORTOFOLIOS: ES_INDEX_USER_PORTOFOLIOS_MAPPINGS}


def create_indices(recreate=False):
    """
    Create ES indices and put their mappings.
    @return: boolean
    """
    es = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

    if recreate:
        for name in INDEX_MAPPINGS:
            es.delete_index(name)

    for index_name in INDEX_MAPPINGS:
        if es.index_exists(index_name):
            logging.info('Index {} already exists'.format(index_name))
            continue

        if not es.create_index(index_name, mappings=INDEX_MAPPINGS[index_name]):
            logging.error('Could not create {} index'.format(index_name))
            return False

    return True


if __name__ == '__main__':
    create_indices(recreate=False)
