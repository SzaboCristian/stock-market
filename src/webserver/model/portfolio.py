"""
Classes for ES minimal portfolio mapping with validation methods.
"""

import json
import time
from datetime import datetime
from typing import List

from util.elasticsearch.es_stock_prices import ESStockPrices
from util.logger.logger import Logger
#####################
# Custom Exceptions #
#####################
from util.utils import DEFAULT_LAST_PRICE_DATE


class AllocationException(Exception):
    pass


class PortfolioException(Exception):
    pass


###########
# Classes #
###########

class Allocation:
    """
    Portfolio allocation entry. ticker and percentage must be specified.
    """

    def __init__(self, ticker=None, percentage=None, allocation_json=None, **kwargs):
        if allocation_json:
            self._ticker = allocation_json.get('ticker', None)
            self._percentage = allocation_json.get('percentage', 0)
            self.__dict__.update(kwargs)

        else:
            self._ticker = ticker
            self._percentage = percentage

        self.validate_allocation()

    def __str__(self) -> str:
        """
        String representation of object.
        @return: str
        """
        return json.dumps(self.get_data())

    def get_data(self) -> dict:
        """
        Returns dict form of object.
        @return: dict
        """
        return dict(ticker=self._ticker, percentage=self._percentage)

    def get_ticker(self) -> str:
        """
        Ticker getter.
        @return: str
        """
        return self._ticker

    def get_percentage(self) -> int:
        """
        Percentage getter.
        @return: int
        """
        return self._percentage

    def set_percentage(self, percentage) -> None:
        """
        Percentage setter.
        @param percentage: int
        @return: None
        """
        self._percentage = percentage

    def validate_allocation(self) -> None:
        """
        Allocation validator.
        @return: None
        """
        valid = self._ticker and 0 < self._percentage <= 100
        if not valid:
            raise AllocationException("Invalid allocation {}".format(self.get_data()))


class Portfolio:
    """
    Portfolio class
    """

    def __init__(self, portfolio_name=None, allocations=None, user_id=None, created_timestamp=None,
                 modified_timestamp=None, portfolio_json=None):
        if portfolio_json:
            self._portfolio_name = portfolio_json.get('portfolio_name', 'default_user_portfolio')
            self._allocations = portfolio_json.get('allocations', [])
            self._user_id = portfolio_json.get('user_id', None)
            self._created_timestamp = portfolio_json.get('created_timestamp', int(time.time()))
            self._modified_timestamp = portfolio_json.get('modified_timestamp', int(time.time()))
        else:
            self._portfolio_name = portfolio_name
            self._allocations = allocations
            self._user_id = user_id
            self._created_timestamp = created_timestamp
            self._modified_timestamp = modified_timestamp
        self.validate_portfolio()

    def __str__(self) -> str:
        """
        Object string representation.
        @return: str
        """
        return json.dumps(self.get_data())

    def get_data(self) -> dict:
        """
        Object dict representation.
        @return: dict
        """
        return dict(portfolio_name=self._portfolio_name,
                    allocations=[allocation.get_data() for allocation in self._allocations],
                    user_id=self._user_id,
                    created_timestamp=self._created_timestamp,
                    modified_timestamp=self._modified_timestamp)

    def get_portfolio_name(self) -> str:
        """
        Portfolio name getter.
        @return: str
        """
        return self._portfolio_name

    def set_portfolio_name(self, portfolio_name) -> None:
        """
        Portfolio name setter.
        @param portfolio_name: string
        @return: None
        """
        self._portfolio_name = portfolio_name

    def get_allocations(self) -> List[Allocation]:
        """
         Allocations getter.
         @return: List[Allocation]
         """
        return self._allocations

    def set_allocations(self, allocations) -> None:
        """
         Allocations setter.
         @param allocations: List[Allocation]
         @return: None
         """
        self._allocations = allocations
        self.validate_portfolio_allocations()

    def get_modified_timestamp(self) -> int:
        """
         Modified timestamp getter.
         @return: int
         """
        return self._modified_timestamp

    def set_modified_timestamp(self, modified_timestamp) -> None:
        """
         Modified timestamp setter.
         @param modified_timestamp: int
         @return: None
         """
        self._modified_timestamp = modified_timestamp

    def backtest(self, start_ts, end_ts) -> dict:
        """
        Backtest portfolio.
        @param start_ts: int
        @param end_ts: int
        @return: dict
        """

        backtest_info = {'start_date': datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d'),
                         'end_date': datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d'),
                         'portfolio_data': {}}

        for allocation in self._allocations:
            ticker = allocation.get_ticker()

            # get first date and price
            first_date_price = ESStockPrices.get_ticker_first_date_price(ticker, start_ts)
            if not first_date_price:
                Logger.exception("No stock prices for ticker {}".format(ticker))
                first_date_price = {DEFAULT_LAST_PRICE_DATE: 0}
            backtest_info['portfolio_data'][ticker] = first_date_price

            # get last date and price
            last_date_price = ESStockPrices.get_ticker_last_date_price(ticker, end_ts)
            if not last_date_price:
                Logger.exception("Could not get last price for ticker {}".format(ticker))
                last_date_price = first_date_price
            backtest_info['portfolio_data'][ticker].update(last_date_price)

        # compute return for each holding
        for ticker in backtest_info['portfolio_data']:
            start_ts, end_ts = min(list(backtest_info['portfolio_data'][ticker].keys())), max(
                list(backtest_info['portfolio_data'][ticker].keys()))

            backtest_info['portfolio_data'][ticker]['return_value_per_share'] = \
                backtest_info['portfolio_data'][ticker][end_ts] - backtest_info['portfolio_data'][ticker][start_ts]

            backtest_info['portfolio_data'][ticker]['return_percentage'] = \
                (100 * backtest_info['portfolio_data'][ticker][end_ts] / backtest_info['portfolio_data'][ticker][
                    start_ts]) - 100

        # compute total return
        backtest_info["total_return_percentage"] = round(
            sum([allocation.get_percentage() / 100 * backtest_info['portfolio_data'][allocation.get_ticker()][
                "return_percentage"] for allocation in self._allocations]), 2)

        return backtest_info

    def validate_portfolio(self) -> None:
        """
        Validate portfolio data fields.
        @return: None
        """
        if not self._user_id:
            raise PortfolioException("No user id set.")

        if not self._portfolio_name:
            raise PortfolioException("No portfolio name set")

        if not self._allocations:
            raise PortfolioException("No allocations set")

        self.validate_portfolio_allocations()

        if not self._created_timestamp:
            raise PortfolioException("No created timestamp set.")

        if not self._modified_timestamp:
            raise PortfolioException("No modified timestamp set.")

    def validate_portfolio_allocations(self) -> None:
        """
        Validate portfolio allocations.
        @return: None
        """
        allocation_percentage = 0
        ticker_tracker = set()
        for allocation in self._allocations:
            if allocation.get_ticker() in ticker_tracker:
                raise AllocationException("Duplicate ticker {}".format(allocation.get_ticker()))

            allocation_percentage += allocation.get_percentage()
            ticker_tracker.add(allocation.get_ticker())

        if allocation_percentage != 100:
            raise PortfolioException("Total allocation percentage must be 100%.")
