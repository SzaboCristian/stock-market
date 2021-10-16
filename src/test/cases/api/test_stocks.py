import unittest

from test.base import InterfaceTestAPI
from webserver.core.stocks_management import StocksManagementAPI


class TestStocksAPI(unittest.TestCase, InterfaceTestAPI):

    def test_missing_params(self):
        self.__test_missing_params_add_stock()
        self.__test_missing_params_delete_stock()
        self.__test_missing_params_update_stock()

    def test_bad_params(self):
        self.__test_bad_params_get_stocks()
        self.__test_bad_params_add_stock()
        self.__test_bad_params_delete_stock()
        self.__test_bad_params_update_stock()

    def test_valid_params(self):
        self.__test_valid_params_get_stocks()
        self.__test_valid_params_add_stock()
        self.__test_valid_params_delete_stock()
        self.__test_valid_params_update_stock()

    def __test_missing_params_add_stock(self):
        pass

    def __test_missing_params_delete_stock(self):
        pass

    def __test_missing_params_update_stock(self):
        pass

    def __test_bad_params_get_stocks(self):
        pass

    def __test_bad_params_add_stock(self):
        pass

    def __test_bad_params_delete_stock(self):
        pass

    def __test_bad_params_update_stock(self):
        pass

    def __test_valid_params_get_stocks(self):
        # get all stocks
        status, data, msg = StocksManagementAPI.get_stocks()
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # get by ticker, existing ticker
        status, data, msg = StocksManagementAPI.get_stocks(ticker="AAPL")
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # get by ticker, inexistent ticker
        status, data, msg = StocksManagementAPI.get_stocks(ticker="INEXISTENT")
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "No stocks found for specified filter.")

    def __test_valid_params_add_stock(self):
        pass

    def __test_valid_params_delete_stock(self):
        pass

    def __test_valid_params_update_stock(self):
        pass
