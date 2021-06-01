import time
from datetime import datetime

import pandas
from yahoofinancials import YahooFinancials

from util import config
from util.logger.logger import Logger

DEFAULT_LAST_PRICE_DATE = "2010-01-01"


def yf_get_historical_price_data_for_ticker(ticker,
                                            start_date=DEFAULT_LAST_PRICE_DATE,
                                            end_date=datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")) -> list:
    """
    Retrieve historical price data using yahoofinancials lib.
    @param ticker: string
    @param start_date: string "YYYY-MM-DD"
    @param end_date: string "YYYY-MM-DD"
    @return: list
    """

    ticker_prices = []
    yahoo_financials = YahooFinancials(ticker)
    data = yahoo_financials.get_historical_price_data(start_date=start_date,
                                                      end_date=end_date,
                                                      time_interval="daily")
    if not data or not data[ticker] or "prices" not in data[ticker]:
        Logger.warning("No price data for {}".format(ticker))
        return []

    prices_dataframe = pandas.DataFrame(data[ticker]["prices"])
    for _, price_entry in prices_dataframe.iterrows():
        ticker_prices.append(
            {"ticker": ticker,
             "date": float(price_entry["date"]),
             "open": float(price_entry["open"]),
             "close": float(price_entry["close"]),
             "high": float(price_entry["high"]),
             "low": float(price_entry["low"]),
             "volume": float(price_entry["volume"])
             }
        )

    return ticker_prices


def get_all_tickers(es_dbi):
    """
    Get all tickers from stocks index.
    @param es_dbi: ElasticsearchDBI object
    @return: list
    """

    # get all tickers from stocks index
    try:
        tickers = es_dbi.search_documents(config.ES_INDEX_STOCKS, query_body={
            "_source": False
        })
        tickers = [es_doc["_id"] for es_doc in tickers["hits"]["hits"]]
    except Exception as exception:
        Logger.exception(str(exception))
        tickers = []

    return sorted(tickers)


def get_last_price_date_for_ticker(ticker, es_dbi) -> str:
    """
    Get last price date from stock_prices index for specified ticker.
    @param ticker: string
    @param es_dbi: ElasticsearchDBI object
    @return: string
    """
    try:
        # get max timestamp for ticker
        last_timestamp_docs = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
            "query": {
                'bool': {
                    'must': [{'term': {'ticker': ticker.lower()}}]}
            },
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        }, size=1)
        if not last_timestamp_docs or not last_timestamp_docs["hits"]["hits"]:
            return DEFAULT_LAST_PRICE_DATE

        if last_timestamp_docs["hits"]["hits"][0]["_source"]["ticker"].lower() != ticker.lower():
            # if ticker name is different => ticker is missing and regepx matched other (ex. ticker A)
            return DEFAULT_LAST_PRICE_DATE

        last_timestamp = int(last_timestamp_docs["hits"]["hits"][0]["_source"]["date"])
        return datetime.fromtimestamp(last_timestamp).strftime("%Y-%m-%d")
    except Exception as exception:
        Logger.exception(exception)

    return DEFAULT_LAST_PRICE_DATE


def get_last_price_date_for_tickers(tickers, es_dbi) -> dict:
    """
    Get last known date from stock_prices index for each ticker
    @param tickers: list
    @param es_dbi: ElasticsearchDBI object
    @return: dict
    """

    # get last price date for each ticker
    ticker_last_price_dates = {}
    for ticker in tickers:
        last_date = get_last_price_date_for_ticker(ticker, es_dbi)
        if last_date:
            ticker_last_price_dates[ticker] = last_date
    return ticker_last_price_dates

