"""
Daemon that keeps stock_prices index up to date. Historical price data is gathered using yahoofinancials library.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time
from datetime import datetime

import pandas
from yahoofinancials import YahooFinancials

import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.logger.logger import Logger

_ONE_HOUR = 3600
_ONE_DAY = 24 * _ONE_HOUR
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

    return tickers


def get_last_price_date_for_ticker(ticker, es_dbi) -> str:
    """
    Get last price date from stock_prices index for specified ticker.
    @param ticker: string
    @param es_dbi: ElasticsearchDBI object
    @return: string
    """

    try:
        # get max timestamp for ticker
        last_timestamp_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
            "query": {
                "bool": {
                    "must": [{"term": {"ticker": ticker.lower()}}]
                }
            },
            "sort": [
                {
                    "date": {
                        "order": "desc"
                    }
                }
            ]
        }, size=1)
        if not last_timestamp_doc["hits"]["hits"]:
            return ""

        last_timestamp = int(last_timestamp_doc["hits"]["hits"][0]["_source"]["date"])
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


def markets_closed_the_day_before() -> bool:
    """
    Check if current day sunday/monday.
    @return: boolean
    """
    return datetime.today().weekday() in [0, 6]


def are_markets_open() -> bool:
    """
    Most markets are closed between 00:00 - 08:00 (Europe time).
    @return: boolean
    """
    return 8 <= datetime.now().hour <= 24


def stock_prices_updater_task() -> None:
    """
    Task updates stock prices using yahoofinancials library.
    @return: None
    """

    es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
    ticker_last_price_dates = {}
    last_ticker_fetch_ts = 0

    while True:
        if markets_closed_the_day_before():
            Logger.info("Markets were closed the day before. No new price info to be found.")
            time.sleep(_ONE_HOUR)
            continue

        if are_markets_open():
            Logger.info("Markets are still open, waiting to close in order to update prices.")
            time.sleep(_ONE_HOUR)
            continue

        start_ts = int(time.time())

        # fetch tickers for first time then refetch every 3 days
        if not ticker_last_price_dates or time.time() - last_ticker_fetch_ts >= 3 * _ONE_DAY:
            tickers = get_all_tickers(es_dbi)
            if tickers:
                ticker_last_price_dates = get_last_price_date_for_tickers(tickers, es_dbi)
                last_ticker_fetch_ts = time.time()

        # update price historical data up to
        yf_now_date = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")

        actions = []
        updated_ticker_last_price_dates = {}
        for ticker in ticker_last_price_dates:
            if ticker_last_price_dates[ticker] != yf_now_date:
                # price history not up to date, get prices
                missing_prices = yf_get_historical_price_data_for_ticker(ticker=ticker,
                                                                         start_date=ticker_last_price_dates[ticker],
                                                                         end_date=yf_now_date)

                if not missing_prices:
                    # no new price data
                    continue

                # add es actions and index
                for missing_price in missing_prices:
                    actions.append({"_index": config.ES_INDEX_STOCK_PRICES,
                                    "_source": missing_price})

                    # do bulk insert
                    if len(actions) >= 1000:
                        es_dbi.bulk(actions, chunk_size=len(actions), max_retries=3)
                        actions = []

                # set last date
                last_price_date = datetime.fromtimestamp(missing_prices[-1]["date"]).strftime("%Y-%m-%d")
                updated_ticker_last_price_dates[ticker] = last_price_date

                Logger.info("Got price history for [{}]: {} -> {}".format(ticker,
                                                                          ticker_last_price_dates[ticker],
                                                                          last_price_date))

        # last batch bulk insert
        if actions:
            es_dbi.bulk(actions, chunk_size=len(actions), max_retries=3)

        # update last price dates
        ticker_last_price_dates.update(updated_ticker_last_price_dates)

        # wait 24h since iteration start
        time.sleep(_ONE_DAY - start_ts)
