import unittest

from tests.unit.base import InterfaceTestAPI
from webserver.core.investment_calculator import InvestmentCalculatorAPI


class TestInvestmentCalculatorAPI(unittest.TestCase, InterfaceTestAPI):
    def test_missing_params(self) -> None:
        """
        Test missing parameters.
        """
        status, data, msg = InvestmentCalculatorAPI.compute_compound_interest()
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def test_bad_params(self) -> None:
        """
        Test bad parameters type.
        """
        status, data, msg = InvestmentCalculatorAPI.compute_compound_interest(
            starting_amount="string",
            yearly_return_rate="100%",
            investment_length_in_years=5,
            additional_yearly_contribution=0,
        )
        self.assertEqual(status, 500)
        self.assertFalse(data)
        self.assertEqual(msg, "Server error. Please contact administrator.")

    def test_valid_params(self) -> None:
        """
        Test valid parameters, positive and negative return.
        """
        # positive return
        status, data, msg = InvestmentCalculatorAPI.compute_compound_interest(
            starting_amount=10000,
            yearly_return_rate=10,
            investment_length_in_years=10,
            additional_yearly_contribution=1000,
        )
        expected_result = {
            "starting_amount": 10000,
            "additional_contribution": 10000,
            "compound_interest": 21874.849202000027,
            "final_amount": 41874.84920200003,
        }

        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(data, expected_result)
        self.assertEqual(msg, "OK")

        # negative return
        status, data, msg = InvestmentCalculatorAPI.compute_compound_interest(
            starting_amount=10000,
            yearly_return_rate=-2,
            investment_length_in_years=5,
            additional_yearly_contribution=1000,
        )
        expected_result = {
            "starting_amount": 10000,
            "additional_contribution": 5000,
            "compound_interest": -1156.8318720000025,
            "final_amount": 13843.168127999998,
        }

        self.assertEqual(status, 200)
        self.assertTrue(data)
        self.assertEqual(data, expected_result)
        self.assertEqual(msg, "OK")
