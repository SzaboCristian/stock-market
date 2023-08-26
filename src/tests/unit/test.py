import os
import unittest

from util import config

config.load_env()

os.environ["DEPLOYED"] = "true"
os.environ["DOCKER_SRC"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from util.logger.logger import Logger

Logger.set_file_logging(file_name="test_apis.log")

from test.cases.api.test_investement_calculator import \
    TestInvestmentCalculatorAPI
from test.cases.api.test_portfolio import TestPortfolioAPI
from test.cases.api.test_stock_prices import TestStockPricesAPI
from test.cases.api.test_stocks import TestStocksAPI

if __name__ == '__main__':
    # run from src level as >> python3.6  -m pytest tests/tests.py
    unittest.main()
