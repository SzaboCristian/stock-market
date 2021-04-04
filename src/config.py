import os

PROJECT_ROOT = '/home/bmf/Desktop/Webapp_project_finance/stock-market'
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

ELASTICSEARCH_HOST = os.environ.get('ELASTIC_HOST', 'localhost')
ELASTICSEARCH_PORT = os.environ.get('ELASTIC_PORT', 9200)
KIBANA_HOST = os.environ.get('KIBANA_HOST', 'localhost')
KIBANA_PORT = os.environ.get('KIBANA_HOST', 5603)

DATASET_STOCKS = os.path.join(PROJECT_ROOT, 'data', 'dataset_stocks.json')
DATASET_STOCK_PRICES = os.path.join(PROJECT_ROOT, 'data', 'dataset_stock_prices.json')

ES_INDEX_STOCKS = 'stocks'
ES_INDEX_STOCK_PRICES = 'stock_prices'
ES_INDEX_PORTOFOLIOS = 'portofolios'
ES_INDEX_USER_PORTOFOLIOS = 'user_portofolios'
