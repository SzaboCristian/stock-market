import unittest

from test.base import InterfaceTestAPI
from webserver.core.portofolio_management import PortofolioManagementAPI


class TestPortofolioAPI(unittest.TestCase, InterfaceTestAPI):

    def setUp(self) -> None:
        self.test_user_id = 'test-user-id'
        self.portofolio_ids = []

    def tearDown(self) -> None:
        for portofolio_id in self.portofolio_ids:
            PortofolioManagementAPI.delete_portofolio(user_id=self.test_user_id, portofolio_id=portofolio_id)

    def test_missing_params(self) -> None:
        """
        Test missing parameters.
        """
        self.__test_missing_params_get_portofolio()
        self.__test_missing_params_add_portofolio()
        self.__test_missing_params_delete_portofolio()
        self.__test_missing_params_update_portofolio()
        self.__test_missing_params_backtest_portofolio()

    def test_bad_params(self) -> None:
        """
        Test bad parameters.
        """
        self.__test_bad_params_get_portofolios()
        self.__test_bad_params_add_portofolio()
        self.__test_bad_params_delete_portofolio()
        self.__test_bad_params_update_portofolio()
        self.__test_bad_params_backtest_portofolio()

    def test_valid_params(self) -> None:
        """
        Test valid parameters.
        """
        self.__test_valid_params_get_portofolios()
        self.__test_valid_params_add_portofolio()
        self.__test_valid_params_delete_portofolio()
        self.__test_valid_params_update_portofolio()
        self.__test_valid_params_backtest_portofolio()

    def __test_missing_params_get_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.get_portofolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_add_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.create_portofolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_delete_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.delete_portofolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_update_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.update_portofolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_backtest_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.backtest_portofolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_get_portofolios(self) -> None:
        status, data, msg = PortofolioManagementAPI.get_portofolio(user_id="test", portofolio_id={"invalid": "type"})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_add_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.create_portofolio(user_id=None, allocations=100)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

        status, data, msg = PortofolioManagementAPI.create_portofolio(user_id=self.test_user_id,
                                                                      allocations=[{'ticker': 'AAPL',
                                                                                    'percentage': 20},
                                                                                   {'ticker': 'TSLA',
                                                                                    'percentage': 50}],
                                                                      test=True)
        self.assertEqual(status, 400)
        self.assertFalse(data)
        self.assertEqual(msg, 'Total allocation percentage must be 100%.')

    def __test_bad_params_delete_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.delete_portofolio(user_id=None, portofolio_id=None)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_update_portofolio(self) -> None:
        # bad data
        status, data, msg = PortofolioManagementAPI.update_portofolio(user_id=None, portofolio_id={"invalid": "type"},
                                                                      new_allocations=100)
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "Portofolio not found.")

        # other user portofolio
        self.__test_valid_params_add_portofolio()
        portofolio_id = self.portofolio_ids[-1]
        new_allocations = [{'ticker': 'AAPL',
                            'percentage': 60},
                           {'ticker': 'TSLA',
                            'percentage': 40}]

        # update protofolio - other user
        status, data, msg = PortofolioManagementAPI.update_portofolio(user_id='other-user-id',
                                                                      portofolio_id=portofolio_id,
                                                                      new_allocations=new_allocations)
        self.assertEqual(status, 401)
        self.assertFalse(data)
        self.assertEqual(msg, 'Cannot update other users\' portofolios')

    def __test_bad_params_backtest_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.backtest_portofolio(user_id=None, portofolio_id=None)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_valid_params_get_portofolios(self) -> None:
        self.__test_valid_params_add_portofolio()
        status, data, msg = PortofolioManagementAPI.get_portofolio(user_id=self.test_user_id,
                                                                   portofolio_id=self.portofolio_ids[-1],
                                                                   test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(self.portofolio_ids[-1], data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_add_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.create_portofolio(user_id=self.test_user_id,
                                                                      allocations=[{'ticker': 'AAPL',
                                                                                    'percentage': 50},
                                                                                   {'ticker': 'TSLA',
                                                                                    'percentage': 50}],
                                                                      test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")
        self.portofolio_ids.append(data['portofolio_id'])

    def __test_valid_params_delete_portofolio(self) -> None:
        self.__test_valid_params_add_portofolio()
        status, data, msg = PortofolioManagementAPI.delete_portofolio(user_id=self.test_user_id,
                                                                      portofolio_id=self.portofolio_ids[-1])
        self.assertEqual(status, 200)
        self.assertEqual(msg, "OK")
        self.portofolio_ids.pop()

    def __test_valid_params_update_portofolio(self) -> None:
        # create portofolio
        self.__test_valid_params_add_portofolio()

        # get data
        portofolio_id = self.portofolio_ids[-1]
        status, data, msg = PortofolioManagementAPI.get_portofolio(user_id=self.test_user_id,
                                                                   portofolio_id=portofolio_id,
                                                                   test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(portofolio_id, data)
        self.assertEqual(msg, "OK")

        new_allocations = [{'ticker': 'AAPL',
                            'percentage': 60},
                           {'ticker': 'TSLA',
                            'percentage': 40}]

        # update protofolio
        status, data, msg = PortofolioManagementAPI.update_portofolio(user_id=self.test_user_id,
                                                                      portofolio_id=portofolio_id,
                                                                      new_allocations=new_allocations)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # check updated data
        status, data, msg = PortofolioManagementAPI.get_portofolio(user_id=self.test_user_id,
                                                                   portofolio_id=portofolio_id,
                                                                   test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(portofolio_id, data)
        self.assertEqual(msg, "OK")
        self.assertEqual(data[portofolio_id]['allocations'], new_allocations)

    def __test_valid_params_backtest_portofolio(self) -> None:
        status, data, msg = PortofolioManagementAPI.backtest_portofolio(user_id=self.test_user_id,
                                                                        portofolio_id=self.portofolio_ids[-1])
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")
