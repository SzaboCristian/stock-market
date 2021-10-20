import time
from datetime import datetime

import pandas
from yahoofinancials import YahooFinancials
from yfinance import Ticker

from util import config
from util.logger.logger import Logger

DEFAULT_LAST_PRICE_DATE = "2010-01-01"

EXCHANGE_NAMES = {"NMS": "National Market System",
                  "BTS": "BitShares BTS",
                  "NGM": "Nordic Growth Market",
                  "PCX": "Pacific Exchange",
                  "PNK": "Pink Sheets (OTC)",
                  "NYQ": "New York Stock Exchange",
                  "NCM": "NCM Nasdaq Commodities",
                  "ASE": "Amman Stock Exchange"
                  }


def get_exchange_name(exchange) -> str:
    """
    Return exchange full name.
    @param exchange: string, exchange abbreviation.
    @return: string
    """
    if exchange not in EXCHANGE_NAMES:
        return exchange
    return EXCHANGE_NAMES[exchange]


def yf_get_info_for_ticker(ticker) -> dict:
    """
    Get ticker info using yfinance and format result.
    @param ticker: string
    @return: dict
    """
    yf_ticker = Ticker(ticker)
    try:
        _ = yf_ticker.info
    except Exception as e:
        Logger.exception("No info for ticker {}. {}".format(ticker, str(e)))
        return {}

    info = dict()
    info["ticker"] = ticker
    info["names"] = [yf_ticker.info.get("longName", None)]
    short_name = yf_ticker.info.get("shortName", None)
    if not info["names"] or (short_name and info["names"][0].lower() != short_name.lower()):
        info["names"].append(short_name.rstrip(" -"))

    info["description"] = yf_ticker.info.get("longBusinessSummary", None)
    info["industry"] = yf_ticker.info.get("industry", None)
    info["sector"] = yf_ticker.info.get("sector", None)
    info["exchanges"] = [yf_ticker.info.get("exchange", None)]
    if info["exchanges"]:
        info["exchanges"] = [get_exchange_name(ex) for ex in info["exchanges"]]
    info["website"] = yf_ticker.info.get("website", None)
    info["tags"] = []

    for key in info:
        if isinstance(info[key], list):
            info[key] = [el for el in info[key] if el]

    info["names"] = list(set(info["names"]))

    tags = []
    if info["industry"]:
        tags.append(info["industry"])
    if info["sector"]:
        tags.append(info["sector"])
    tags = list(set(tags))

    if tags:
        info["tags"] = tags

    return info


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
    tickers = set()
    try:
        for es_doc in es_dbi.scroll_search_documents_generator(config.ES_INDEX_STOCKS, query_body={
            "_source": False
        }):
            tickers.add(es_doc['_id'])
    except Exception as exception:
        Logger.exception(str(exception))

    return sorted(list(tickers))


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
            "_source": ["ticker", "date"],
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
