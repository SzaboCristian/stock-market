import unittest

from tests.unit.base import InterfaceTestAPI
from webserver.core.stocks_management import StocksManagementAPI


class TestStocksAPI(unittest.TestCase, InterfaceTestAPI):

    def setUp(self) -> None:
        self.test_ticker = "AAPL"

    def test_missing_params(self) -> None:
        """
        Test missing parameters.
        """
        self.__test_missing_params_add_stock()
        self.__test_missing_params_delete_stock()
        self.__test_missing_params_update_stock()

    def test_bad_params(self) -> None:
        """
        Test bad parameters.
        """
        self.__test_bad_params_get_stocks()
        self.__test_bad_params_add_stock()
        self.__test_bad_params_delete_stock()
        self.__test_bad_params_update_stock()

    def test_valid_params(self) -> None:
        """
        Test valid parameters.
        """
        self.__test_valid_params_get_stocks()
        self.__test_valid_params_add_stock()
        self.__test_valid_params_delete_stock()
        self.__test_valid_params_update_stock()

    def __test_missing_params_add_stock(self) -> None:
        status, data, msg = StocksManagementAPI.add_stock()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_delete_stock(self) -> None:
        status, data, msg = StocksManagementAPI.delete_stock()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_update_stock(self) -> None:
        status, data, msg = StocksManagementAPI.update_stock_info()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_get_stocks(self) -> None:
        status, data, msg = StocksManagementAPI.get_stocks(ticker={"invalid": "type"})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_add_stock(self) -> None:
        status, data, msg = StocksManagementAPI.add_stock(ticker={"invalid": "type"})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_delete_stock(self) -> None:
        status, data, msg = StocksManagementAPI.delete_stock(ticker={"invalid": "type"})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_update_stock(self) -> None:
        status, data, msg = StocksManagementAPI.update_stock_info(ticker={"invalid": "type"}, updated_info=None)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_valid_params_get_stocks(self) -> None:
        # get all stocks
        status, data, msg = StocksManagementAPI.get_stocks()
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # get by ticker, existing ticker
        status, data, msg = StocksManagementAPI.get_stocks(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # get by ticker, inexistent ticker
        status, data, msg = StocksManagementAPI.get_stocks(ticker="INEXISTENT")
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "No stocks found for specified filter.")

    def __test_valid_params_add_stock(self) -> None:
        status, data, msg = StocksManagementAPI.add_stock(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_delete_stock(self) -> None:
        # get existing stock
        status, data, msg = StocksManagementAPI.get_stocks(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # delete stock
        status, data, msg = StocksManagementAPI.delete_stock(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # check deleted
        status, data, msg = StocksManagementAPI.get_stocks(ticker=self.test_ticker)
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "No stocks found for specified filter.")

        # reinsert
        status, data, msg = StocksManagementAPI.add_stock(ticker=self.test_ticker)
        self.assertEqual(status, 201)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_update_stock(self) -> None:
        # get stock info
        status, stock_info, msg = StocksManagementAPI.get_stocks(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(stock_info)
        self.assertEqual(msg, "OK")

        # update info
        stock_info["updated"] = True
        status, updated, msg = StocksManagementAPI.update_stock_info(ticker=self.test_ticker,
                                                                     updated_info=stock_info)
        self.assertEqual(status, 200)
        self.assertTrue(updated)
        self.assertEqual(msg, "OK")

        # check updated
        # get stock info
        status, updated_info, msg = StocksManagementAPI.get_stocks(ticker=self.test_ticker)
        self.assertEqual(status, 200)
        self.assertTrue(updated_info)
        self.assertEqual(msg, "OK")

        self.assertIn(self.test_ticker, updated_info)
        self.assertIn("updated", updated_info[self.test_ticker])
        self.assertTrue(updated_info[self.test_ticker]["updated"])

        # delete/reinsert stock
        self.__test_valid_params_delete_stock()
