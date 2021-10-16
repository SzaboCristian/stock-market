import unittest

from test.base import InterfaceTestAPI
from webserver.core.stock_prices_management import StockPricesManagementAPI


class TestStockPricesAPI(unittest.TestCase, InterfaceTestAPI):

    def setUp(self) -> None:
        self.test_ticker = "AAPL"

    def test_missing_params(self) -> None:
        """
        Test missing parameters.
        """
        self.__test_missing_params_get_stock_pricess()
        self.__test_missing_params_add_stock_prices()
        self.__test_missing_params_delete_stock_prices()

    def test_bad_params(self) -> None:
        """
        Test bad parameters.
        """
        self.__test_bad_params_get_stock_pricess()
        self.__test_bad_params_add_stock_prices()
        self.__test_bad_params_delete_stock_prices()

    def test_valid_params(self) -> None:
        """
        Test valid parameters.
        """
        self.__test_valid_params_get_stock_pricess()
        self.__test_valid_params_add_stock_prices()
        self.__test_valid_params_delete_stock_prices()

    def __test_missing_params_get_stock_pricess(self) -> None:
        status, data, msg = StockPricesManagementAPI.get_price_history_for_ticker()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_add_stock_prices(self) -> None:
        status, data, msg = StockPricesManagementAPI.add_price_history_for_stock()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_delete_stock_prices(self) -> None:
        status, data, msg = StockPricesManagementAPI.delete_price_history_for_stock()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_get_stock_pricess(self) -> None:
        status, data, msg = StockPricesManagementAPI.get_price_history_for_ticker({"invalid": {"ticker": {"type"}}})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_add_stock_prices(self) -> None:
        status, data, msg = StockPricesManagementAPI.add_price_history_for_stock({"invalid": {"ticker": {"type"}}})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_delete_stock_prices(self) -> None:
        status, data, msg = StockPricesManagementAPI.delete_price_history_for_stock({"invalid": {"ticker": {"type"}}})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_valid_params_get_stock_pricess(self) -> None:
        status, data, msg = StockPricesManagementAPI.get_price_history_for_ticker(ticker=self.test_ticker,
                                                                                  start='LAST_YEAR')
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_add_stock_prices(self) -> None:
        status, data, msg = StockPricesManagementAPI.add_price_history_for_stock(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_delete_stock_prices(self) -> None:
        # get stock prices
        status, data, msg = StockPricesManagementAPI.get_price_history_for_ticker(ticker=self.test_ticker,
                                                                                  start='LAST_YEAR')
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # delete stock prices
        status, data, msg = StockPricesManagementAPI.delete_price_history_for_stock(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # check stock prices deleted
        status, data, msg = StockPricesManagementAPI.get_price_history_for_ticker(ticker=self.test_ticker,
                                                                                  start='LAST_YEAR')
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "No price history for ticker {} for specified time range.".format(self.test_ticker))

        # add stock prices
        status, data, msg = StockPricesManagementAPI.add_price_history_for_stock(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")
