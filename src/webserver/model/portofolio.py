"""
Classes for ES minimal portofolio mapping with validation methods.
"""

import json
import time
from datetime import datetime
from typing import List

from util import config


#####################
# Custom Exceptions #
#####################

class AllocationException(Exception):
    pass


class PortofolioException(Exception):
    pass


###########
# Classes #
###########

class Allocation:
    """
    Portofolio allocation entry. ticker and percentage must be specified.
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


class Portofolio:
    """
    Portofolio class
    """

    def __init__(self, portofolio_name=None, allocations=None, user_id=None, created_timestamp=None,
                 modified_timestamp=None, portofolio_json=None):
        if portofolio_json:
            self._portofolio_name = portofolio_json.get('portofolio_name', 'default_user_portofolio')
            self._allocations = portofolio_json.get('allocations', [])
            self._user_id = portofolio_json.get('user_id', None)
            self._created_timestamp = portofolio_json.get('created_timestamp', int(time.time()))
            self._modified_timestamp = portofolio_json.get('modified_timestamp', int(time.time()))
        else:
            self._portofolio_name = portofolio_name
            self._allocations = allocations
            self._user_id = user_id
            self._created_timestamp = created_timestamp
            self._modified_timestamp = modified_timestamp
        self.validate_portofolio()

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
        return dict(portofolio_name=self._portofolio_name,
                    allocations=[allocation.get_data() for allocation in self._allocations],
                    user_id=self._user_id,
                    created_timestamp=self._created_timestamp,
                    modified_timestamp=self._modified_timestamp)

    def get_portofolio_name(self) -> str:
        """
        Portofolio name getter.
        @return: str
        """
        return self._portofolio_name

    def set_portofolio_name(self, portofolio_name) -> None:
        """
        Portofolio name setter.
        @param portofolio_name: string
        @return: None
        """
        self._portofolio_name = portofolio_name

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
        self.validate_portofolio_allocations()

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

    def backtest(self, es_dbi, start_ts, end_ts) -> dict:
        """
        Backtest portofolio.
        @param es_dbi: ElasticsearchDBI object
        @param start_ts: int
        @param end_ts: int
        @return: dict
        """

        backtest_info = {'start_date': datetime.fromtimestamp(start_ts).strftime('%Y-%m-%d'),
                         'end_date': datetime.fromtimestamp(end_ts).strftime('%Y-%m-%d'),
                         'portofolio_data': {}}

        for allocation in self._allocations:
            ticker = allocation.get_ticker()
            es_first_price_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
                'query': {'bool': {'must': [{'term': {'ticker': ticker.lower()}},
                                            {'range': {'date': {'gte': start_ts}}}]}},
                "sort": [
                    {
                        "date": {
                            "order": "asc"
                        }
                    }
                ]
            }, size=1)
            es_first_price_doc = es_first_price_doc["hits"]["hits"][0]
            backtest_info['portofolio_data'][ticker] = {es_first_price_doc["_source"]["date"]: float(
                es_first_price_doc["_source"]["close"])}

            es_last_price_doc = es_dbi.search_documents(config.ES_INDEX_STOCK_PRICES, query_body={
                'query': {'bool': {'must': [{'term': {'ticker': ticker.lower()}},
                                            {'range': {'date': {'lte': end_ts}}}]}},
                "sort": [
                    {
                        "date": {
                            "order": "desc"
                        }
                    }
                ]
            }, size=1)
            es_last_price_doc = es_last_price_doc["hits"]["hits"][0]
            backtest_info['portofolio_data'][ticker][es_last_price_doc["_source"]["date"]] = float(
                es_last_price_doc["_source"]["close"])

        # compute return for each holding
        for ticker in backtest_info['portofolio_data']:
            start_ts, end_ts = min(list(backtest_info['portofolio_data'][ticker].keys())), max(
                list(backtest_info['portofolio_data'][ticker].keys()))

            backtest_info['portofolio_data'][ticker]['return_value_per_share'] = \
                backtest_info['portofolio_data'][ticker][end_ts] - backtest_info['portofolio_data'][ticker][start_ts]

            backtest_info['portofolio_data'][ticker]['return_percentage'] = \
                (100 * backtest_info['portofolio_data'][ticker][end_ts] / backtest_info['portofolio_data'][ticker][
                    start_ts]) - 100

        # compute total return
        backtest_info["total_return_percentage"] = round(
            sum([allocation.get_percentage() / 100 * backtest_info['portofolio_data'][allocation.get_ticker()][
                "return_percentage"] for allocation in self._allocations]), 2)

        return backtest_info

    def validate_portofolio(self) -> None:
        """
        Validate portofolio data fields.
        @return: None
        """
        if not self._user_id:
            raise PortofolioException("No user id set.")

        if not self._portofolio_name:
            raise PortofolioException("No portofolio name set")

        if not self._allocations:
            raise PortofolioException("No allocations set")

        self.validate_portofolio_allocations()

        if not self._created_timestamp:
            raise PortofolioException("No created timestamp set.")

        if not self._modified_timestamp:
            raise PortofolioException("No modified timestamp set.")

    def validate_portofolio_allocations(self) -> None:
        """
        Validate portofolio allocations.
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
            raise PortofolioException("Total allocation percentage must be 100%.")
