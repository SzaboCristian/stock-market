class InvestmentCalculatorAPI:

    @staticmethod
    def compute_compound_interest(starting_amount, yearly_return_rate, investment_length_in_years,
                                  additional_yearly_contribution=0, additional_at_end_of_year=True) -> tuple:
        """
        Compute compound interest and final amount of investment.
        @param starting_amount: int, initial deposit
        @param yearly_return_rate: float, yearly return rate
        @param investment_length_in_years: int, investment length in years
        @param additional_yearly_contribution: int, additional yearly contribution
        @param additional_at_end_of_year: boolean, flag for additional contribution (start of end of each year)
        @return: tuple
        """

        # compute final amount
        if not additional_yearly_contribution:
            final_amount = starting_amount * (pow((1 + yearly_return_rate / 100), investment_length_in_years))
        else:
            final_amount = starting_amount
            for year in range(investment_length_in_years):
                if additional_at_end_of_year:
                    final_amount = (1 + yearly_return_rate / 100) * final_amount + additional_yearly_contribution
                else:
                    final_amount = (1 + yearly_return_rate / 100) * (final_amount + additional_yearly_contribution)

        # compute compound interest
        compound_interest = final_amount - (
                starting_amount + investment_length_in_years * additional_yearly_contribution)

        return 200, {
            "starting_amount": starting_amount,
            "additional_contribution": investment_length_in_years * additional_yearly_contribution,
            "compound_interest": compound_interest,
            "final_amount": final_amount}, "OK"

    @staticmethod
    def compute_return_rate(target, starting_amount, investment_length_in_years, additional_yearly_contribution=0,
                            additional_at_end_of_year=True):
        """
        TODO
        @param target:
        @param starting_amount:
        @param investment_length_in_years:
        @param additional_yearly_contribution:
        @param additional_at_end_of_year:
        @return:
        """

        # TODO
        if not additional_yearly_contribution:
            ror = 'UNIMPLEMENTED'
        else:
            ror = 'UNIMPLEMENTED'

        return 200, {"starting_amount": starting_amount,
                     "target": target,
                     "investment_length_in_years": investment_length_in_years,
                     "return_rate": ror}, "OK"
