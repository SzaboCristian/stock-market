import unittest

from tests.unit.base import InterfaceTestAPI
from webserver.core.portfolio_management import PortfolioManagementAPI


class TestPortfolioAPI(unittest.TestCase, InterfaceTestAPI):

    def setUp(self) -> None:
        self.test_user_id = 'tests-user-id'
        self.portfolio_ids = []

    def tearDown(self) -> None:
        for portfolio_id in self.portfolio_ids:
            PortfolioManagementAPI.delete_portfolio(user_id=self.test_user_id, portfolio_id=portfolio_id)

    def test_missing_params(self) -> None:
        """
        Test missing parameters.
        """
        self.__test_missing_params_get_portfolio()
        self.__test_missing_params_add_portfolio()
        self.__test_missing_params_delete_portfolio()
        self.__test_missing_params_update_portfolio()
        self.__test_missing_params_backtest_portfolio()

    def test_bad_params(self) -> None:
        """
        Test bad parameters.
        """
        self.__test_bad_params_get_portfolios()
        self.__test_bad_params_add_portfolio()
        self.__test_bad_params_delete_portfolio()
        self.__test_bad_params_update_portfolio()
        self.__test_bad_params_backtest_portfolio()

    def test_valid_params(self) -> None:
        """
        Test valid parameters.
        """
        self.__test_valid_params_get_portfolios()
        self.__test_valid_params_add_portfolio()
        self.__test_valid_params_delete_portfolio()
        self.__test_valid_params_update_portfolio()
        self.__test_valid_params_backtest_portfolio()

    def __test_missing_params_get_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.get_portfolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_add_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.create_portfolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_delete_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.delete_portfolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_update_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.update_portfolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_missing_params_backtest_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.backtest_portfolio()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_get_portfolios(self) -> None:
        status, data, msg = PortfolioManagementAPI.get_portfolio(user_id="tests", portfolio_id={"invalid": "type"})
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_add_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.create_portfolio(user_id=None, allocations=100)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

        status, data, msg = PortfolioManagementAPI.create_portfolio(user_id=self.test_user_id,
                                                                    allocations=[{'ticker': 'AAPL',
                                                                                  'percentage': 20},
                                                                                 {'ticker': 'TSLA',
                                                                                  'percentage': 50}],
                                                                    test=True)
        self.assertEqual(status, 400)
        self.assertFalse(data)
        self.assertEqual(msg, 'Total allocation percentage must be 100%.')

    def __test_bad_params_delete_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.delete_portfolio(user_id=None, portfolio_id=None)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_bad_params_update_portfolio(self) -> None:
        # bad data
        status, data, msg = PortfolioManagementAPI.update_portfolio(user_id=None, portfolio_id={"invalid": "type"},
                                                                    new_allocations=100)
        self.assertEqual(status, 404)
        self.assertFalse(data)
        self.assertEqual(msg, "Portfolio not found.")

        # other user portfolio
        self.__test_valid_params_add_portfolio()
        portfolio_id = self.portfolio_ids[-1]
        new_allocations = [{'ticker': 'AAPL',
                            'percentage': 60},
                           {'ticker': 'TSLA',
                            'percentage': 40}]

        # update protofolio - other user
        status, data, msg = PortfolioManagementAPI.update_portfolio(user_id='other-user-id',
                                                                    portfolio_id=portfolio_id,
                                                                    new_allocations=new_allocations)
        self.assertEqual(status, 401)
        self.assertFalse(data)
        self.assertEqual(msg, 'Cannot update other users\' portfolios')

    def __test_bad_params_backtest_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.backtest_portfolio(user_id=None, portfolio_id=None)
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def __test_valid_params_get_portfolios(self) -> None:
        self.__test_valid_params_add_portfolio()
        status, data, msg = PortfolioManagementAPI.get_portfolio(user_id=self.test_user_id,
                                                                 portfolio_id=self.portfolio_ids[-1],
                                                                 test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(self.portfolio_ids[-1], data)
        self.assertEqual(msg, "OK")

    def __test_valid_params_add_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.create_portfolio(user_id=self.test_user_id,
                                                                    allocations=[{'ticker': 'AAPL',
                                                                                  'percentage': 50},
                                                                                 {'ticker': 'TSLA',
                                                                                  'percentage': 50}],
                                                                    test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")
        self.portfolio_ids.append(data['portfolio_id'])

    def __test_valid_params_delete_portfolio(self) -> None:
        self.__test_valid_params_add_portfolio()
        status, data, msg = PortfolioManagementAPI.delete_portfolio(user_id=self.test_user_id,
                                                                    portfolio_id=self.portfolio_ids[-1])
        self.assertEqual(status, 200)
        self.assertEqual(msg, "OK")
        self.portfolio_ids.pop()

    def __test_valid_params_update_portfolio(self) -> None:
        # create portfolio
        self.__test_valid_params_add_portfolio()

        # get data
        portfolio_id = self.portfolio_ids[-1]
        status, data, msg = PortfolioManagementAPI.get_portfolio(user_id=self.test_user_id,
                                                                 portfolio_id=portfolio_id,
                                                                 test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(portfolio_id, data)
        self.assertEqual(msg, "OK")

        new_allocations = [{'ticker': 'AAPL',
                            'percentage': 60},
                           {'ticker': 'TSLA',
                            'percentage': 40}]

        # update protofolio
        status, data, msg = PortfolioManagementAPI.update_portfolio(user_id=self.test_user_id,
                                                                    portfolio_id=portfolio_id,
                                                                    new_allocations=new_allocations)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")

        # check updated data
        status, data, msg = PortfolioManagementAPI.get_portfolio(user_id=self.test_user_id,
                                                                 portfolio_id=portfolio_id,
                                                                 test=True)
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertIn(portfolio_id, data)
        self.assertEqual(msg, "OK")
        self.assertEqual(data[portfolio_id]['allocations'], new_allocations)

    def __test_valid_params_backtest_portfolio(self) -> None:
        status, data, msg = PortfolioManagementAPI.backtest_portfolio(user_id=self.test_user_id,
                                                                      portfolio_id=self.portfolio_ids[-1])
        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(msg, "OK")
