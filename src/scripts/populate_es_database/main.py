"""
Script populates stocks and stock_prices Elasticsearch indices.
"""

__version__ = '0.0.1'
__author__ = 'Szabo Cristian'

import json
import os
import sys
import time
from datetime import datetime

import pandas
from yahoofinancials import YahooFinancials

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.logger.logger import Logger

ES_BATCH_SIZE = 1000


def populate_stocks_from_dataset_file(es_dbi) -> bool:
    """
    Read dataset file and index to stocks index
    @param es_dbi: ElasticsearchDBI object
    @return: boolean
    """
    if not os.path.isfile(config.DATASET_STOCKS):
        Logger.error('File {} does not exist'.format(config.DATASET_STOCKS))
        return False

    es_actions = []
    success, failed = 0, 0
    start_time = time.time()
    with open(config.DATASET_STOCKS, 'r') as ds_file:
        stock_entry = ds_file.readline()
        while stock_entry:
            stock_entry = json.loads(stock_entry)
            es_actions.append({
                '_id': stock_entry['ticker'],
                '_index': config.ES_INDEX_STOCKS,
                '_source': {k: v for k, v in stock_entry.items() if k != 'ticker'}
            })
            if len(es_actions) >= ES_BATCH_SIZE:
                batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
                success += batch_success
                failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)
                es_actions = []

            stock_entry = ds_file.readline()

    if es_actions:
        batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
        success += batch_success
        failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)

    Logger.info('Done populated index {}. Success: {}; Failed: {}; Time {} seconds.'.format(
        config.ES_INDEX_STOCKS, success, failed, round(time.time() - start_time, 2)))
    return True


def populate_stock_prices_from_dataset_file(es_dbi) -> bool:
    """
    Read dataset file and index to stock prices index. (faster)
    @param es_dbi: ElasticsearchDBI
    @return: boolean
    """
    if not os.path.isfile(config.DATASET_STOCK_PRICES):
        Logger.error('File {} does not exist'.format(config.DATASET_STOCK_PRICES))
        return False

    es_actions = []
    success, failed = 0, 0
    start_time = time.time()
    with open(config.DATASET_STOCK_PRICES, 'r') as ds_file:
        stock_entry = ds_file.readline()
        while stock_entry:
            es_actions.append({
                '_index': config.ES_INDEX_STOCK_PRICES,
                '_source': json.loads(stock_entry)
            })
            if len(es_actions) >= ES_BATCH_SIZE:
                batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
                success += batch_success
                failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)
                es_actions = []

            stock_entry = ds_file.readline()

    if es_actions:
        batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
        success += batch_success
        failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)

    Logger.info('Done populated index {}. Success: {}; Failed: {}; Time {} seconds.'.format(
        config.ES_INDEX_STOCK_PRICES, success, failed, round(time.time() - start_time, 2)))
    return True


def yf_get_historical_price_data_for_ticker(ticker, start_date='2010-01-01',
                                            end_date=datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')) -> list:
    """
    Retrieve historical price data using yahoofinancials lib.
    @param ticker: string
    @param start_date: string 'YYYY-MM-DD'
    @param end_date: string 'YYYY-MM-DD'
    @return: list
    """

    ticker_prices = []
    yahoo_financials = YahooFinancials(ticker)
    data = yahoo_financials.get_historical_price_data(start_date=start_date,
                                                      end_date=end_date,
                                                      time_interval='daily')
    if not data or not data[ticker] or 'prices' not in data[ticker]:
        Logger.warning('No price data for {}'.format(ticker))
        return []

    prices_dataframe = pandas.DataFrame(data[ticker]['prices'])
    for _, price_entry in prices_dataframe.iterrows():
        ticker_prices.append(
            {'ticker': ticker,
             'date': float(price_entry['date']),
             'open': float(price_entry['open']),
             'close': float(price_entry['close']),
             'high': float(price_entry['high']),
             'low': float(price_entry['low']),
             'volume': float(price_entry['volume'])
             }
        )

    return ticker_prices


def yf_populate_stock_prices(es_dbi) -> bool:
    """
    Read stocks index and get historical price data for each ticker using yfinance library.
    Results are indexed in stock_prices index. (slow)
    @param es_dbi: ElasticsearchDBI
    @return: boolean
    """

    es_actions = []
    success, failed = 0, 0
    start_time = time.time()

    for es_doc in es_dbi.scroll_search_documents_generator(config.ES_INDEX_STOCKS):
        ticker = es_doc['_id'].upper()
        prices = yf_get_historical_price_data_for_ticker(ticker)
        if not prices:
            Logger.warning('No prices for ticker {}'.format(ticker))
            continue

        for price in prices:
            es_actions.append({
                '_index': config.ES_INDEX_STOCK_PRICES,
                '_source': price
            })
            if len(es_actions) >= ES_BATCH_SIZE:
                batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
                success += batch_success
                failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)
                es_actions = []

    if es_actions:
        batch_success, batch_failed = es_dbi.bulk(es_actions, chunk_size=len(es_actions), max_retries=3)
        success += batch_success
        failed += len(batch_failed) if isinstance(batch_failed, list) else len(es_actions)

    Logger.info('Done populated index {}. Success: {}; Failed: {}; Time {} seconds.'.format(
        config.ES_INDEX_STOCK_PRICES, success, failed, round(time.time() - start_time, 2)))
    return True


def populate_es_indices():
    """
    Main function. Populates elasticsearch index "stocks" from dataset file. Index "stock_prices" is then populated
    from dataset file or using yahoofinancials library if dataset is missing.
    @return: None
    """
    elasticsearch_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)

    # populate from dataset
    success_stocks = populate_stocks_from_dataset_file(elasticsearch_dbi)
    if not success_stocks:
        Logger.error('Indexing {} failed'.format(config.ES_INDEX_STOCKS))
        sys.exit(-1)

    # populate from dataset
    success_stock_prices = populate_stock_prices_from_dataset_file(elasticsearch_dbi)
    if not success_stock_prices:
        Logger.error('Indexing {} from dataset failed. Indexing using yahoofinancials...'
                     .format(config.ES_INDEX_STOCK_PRICES))

        # try using yahoofinancials
        success_stock_prices = yf_populate_stock_prices(elasticsearch_dbi)
        if not success_stock_prices:
            Logger.error('Indexing {} failed.'.format(config.ES_INDEX_STOCK_PRICES))
            sys.exit(-1)


if __name__ == '__main__':
    populate_es_indices()
