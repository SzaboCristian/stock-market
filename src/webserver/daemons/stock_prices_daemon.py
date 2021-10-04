"""
Daemon that keeps stock_prices index up to date. Historical price data is gathered using yahoofinancials library.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

import time
from datetime import datetime

from util import config
from util.elasticsearch.elasticsearch_dbi import ElasticsearchDBI
from util.logger.logger import Logger
from util.utils import get_all_tickers, get_last_price_date_for_tickers, yf_get_historical_price_data_for_ticker

_ONE_HOUR = 3600
_ONE_DAY = 24 * _ONE_HOUR


def markets_closed_the_day_before() -> bool:
    """
    Check if current day sunday/monday.
    @return: boolean
    """
    return datetime.today().weekday() in [0, 6]


def are_any_markets_open() -> bool:
    """
    Most markets are closed between 00:00 - 08:00 (Europe time) and on weekends.
    @return: boolean
    """
    return datetime.today().weekday() not in [5, 6] and 8 <= datetime.now().hour <= 24


def should_update_stock_prices() -> bool:
    if markets_closed_the_day_before():
        Logger.info("Markets were closed the day before. No new price info to be found.")
        return False

    if are_any_markets_open():
        Logger.info("Markets are still open, waiting to close in order to update prices.")
        return False

    return True


def stock_prices_updater_task() -> None:
    """
    Task updates stock prices using yahoofinancials library.
    @return: None
    """

    es_dbi = ElasticsearchDBI.get_instance(config.ELASTICSEARCH_HOST, config.ELASTICSEARCH_PORT)
    ticker_last_price_dates = {}
    last_ticker_fetch_ts = 0
    update_cnt = 0

    while True:
        # always update on daemon startup and then at the end of each day when markets were open
        if update_cnt != 0 and not should_update_stock_prices():
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
        update_cnt += 1
