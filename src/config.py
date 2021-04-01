import os

PROJECT_ROOT = '/home/bmf/Desktop/Webapp_project_finance/stock-market'

ELASTICSEARCH_HOST = 'localhost'
ELASTICSEARCH_PORT = 9200

DATASET_STOCKS = os.path.join(PROJECT_ROOT, 'data', 'dataset_stocks.json')
DATASET_STOCK_PRICES = os.path.join(PROJECT_ROOT, 'data', 'dataset_stock_prices.json')

ES_INDEX_STOCKS = 'stocks'
ES_INDEX_STOCK_PRICES = 'stock_prices'
ES_INDEX_PORTOFOLIOS = 'portofolios'
ES_INDEX_USER_PORTOFOLIOS = 'user_portofolios'
