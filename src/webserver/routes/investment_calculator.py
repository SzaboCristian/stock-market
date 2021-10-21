"""
API Route class.
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from flask_restplus import Resource

from webserver import decorators
from webserver.core.investment_calculator import InvestmentCalculatorAPI
from webserver.flask_rest import FlaskRestPlusApi
from webserver.responses import response_400, response
from webserver.routes.utils import api_param_query, get_request_parameter

api = FlaskRestPlusApi.get_instance()


class RouteInvestmentCalculatorCompoundInterest(Resource):
    method_decorators = [decorators.webserver_logger]

    @staticmethod
    @api.doc(description="Compute compound interest.")
    @api.doc(params={
        "starting_amount": api_param_query(required=True,
                                           description="Starting amount in USD",
                                           type="integer"),
        "yearly_return_rate": api_param_query(required=True,
                                              description="Yearly return (percentage): float"),
        "investment_length_in_years": api_param_query(required=True,
                                                      description="Investment length: int",
                                                      type="integer"),
        "additional_yearly_contribution": api_param_query(required=False,
                                                          description="Additional contribution",
                                                          type="integer",
                                                          default=0),
        'additional_at_end_of_year': api_param_query(required=False,
                                                     description="Compound at the end of the year flag.",
                                                     type="boolean",
                                                     default=True),
    }
    )
    @api.doc(responses={
        200: "OK",
        400: "Param <> is required"
    })
    def get() -> response:
        starting_amount, msg = get_request_parameter("starting_amount", expected_type=int, required=True)
        if starting_amount is None:
            return response_400(msg)

        yearly_return_rate, msg = get_request_parameter("yearly_return_rate", expected_type=float, required=True)
        if yearly_return_rate is None:
            return response_400(msg)

        investment_length_in_years, msg = get_request_parameter("investment_length_in_years", expected_type=int,
                                                                required=True)
        if investment_length_in_years is None:
            return response_400(msg)
        if investment_length_in_years < 1:
            return response_400("Investment length must be greater or equal to 1")

        additional_yearly_contribution = get_request_parameter("additional_yearly_contribution", expected_type=int,
                                                               required=False)
        if additional_yearly_contribution is None:
            additional_yearly_contribution = 0

        additional_at_end_of_year = get_request_parameter("additional_at_end_of_year", expected_type=bool,
                                                          required=False)
        if additional_at_end_of_year is None:
            additional_at_end_of_year = True

        return response(*InvestmentCalculatorAPI.compute_compound_interest(
            starting_amount=starting_amount,
            yearly_return_rate=yearly_return_rate,
            investment_length_in_years=investment_length_in_years,
            additional_yearly_contribution=additional_yearly_contribution,
            additional_at_end_of_year=additional_at_end_of_year))
