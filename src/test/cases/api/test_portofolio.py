import unittest

from test.base import InterfaceTestAPI


class TestPortofolioAPI(unittest.TestCase, InterfaceTestAPI):

    def test_missing_params(self):
        self.__test_missing_params_add_portofolio()
        self.__test_missing_params_delete_portofolio()
        self.__test_missing_params_update_portofolio()

    def test_bad_params(self):
        self.__test_bad_params_get_portofolios()
        self.__test_bad_params_add_portofolio()
        self.__test_bad_params_delete_portofolio()
        self.__test_bad_params_update_portofolio()

    def test_valid_params(self):
        self.__test_valid_params_get_portofolios()
        self.__test_valid_params_add_portofolio()
        self.__test_valid_params_delete_portofolio()
        self.__test_valid_params_update_portofolio()

    def __test_missing_params_add_portofolio(self):
        pass

    def __test_missing_params_delete_portofolio(self):
        pass

    def __test_missing_params_update_portofolio(self):
        pass

    def __test_bad_params_get_portofolios(self):
        pass

    def __test_bad_params_add_portofolio(self):
        pass

    def __test_bad_params_delete_portofolio(self):
        pass

    def __test_bad_params_update_portofolio(self):
        pass

    def __test_valid_params_get_portofolios(self):
        pass

    def __test_valid_params_add_portofolio(self):
        pass

    def __test_valid_params_delete_portofolio(self):
        pass

    def __test_valid_params_update_portofolio(self):
        pass
