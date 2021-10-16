import unittest

from test.base import InterfaceTestAPI


class TestStockPricesAPI(unittest.TestCase, InterfaceTestAPI):
    
    def test_missing_params(self):
        self.__test_missing_params_add_stock_prices()
        self.__test_missing_params_delete_stock_prices()
        self.__test_missing_params_update_stock_prices()

    def test_bad_params(self):
        self.__test_bad_params_get_stock_pricess()
        self.__test_bad_params_add_stock_prices()
        self.__test_bad_params_delete_stock_prices()
        self.__test_bad_params_update_stock_prices()

    def test_valid_params(self):
        self.__test_valid_params_get_stock_pricess()
        self.__test_valid_params_add_stock_prices()
        self.__test_valid_params_delete_stock_prices()
        self.__test_valid_params_update_stock_prices()

    def __test_missing_params_add_stock_prices(self):
        pass

    def __test_missing_params_delete_stock_prices(self):
        pass

    def __test_missing_params_update_stock_prices(self):
        pass

    def __test_bad_params_get_stock_pricess(self):
        pass

    def __test_bad_params_add_stock_prices(self):
        pass

    def __test_bad_params_delete_stock_prices(self):
        pass

    def __test_bad_params_update_stock_prices(self):
        pass

    def __test_valid_params_get_stock_pricess(self):
        pass

    def __test_valid_params_add_stock_prices(self):
        pass

    def __test_valid_params_delete_stock_prices(self):
        pass

    def __test_valid_params_update_stock_prices(self):
        pass
