from webserver.flask_rest import FlaskApp, FlaskRestPlusApi
from webserver.routes.investment_calculator import RouteInvestmentCalculatorReturnRate, \
    RouteInvestmentCalculatorCompoundInterest
from webserver.routes.stock_prices import RouteStockPrices
from webserver.routes.stocks import RouteStocks
from webserver.routes.users import RouteUsers

# create flask app
flask_app = FlaskApp.get_instance()
flask_api = FlaskRestPlusApi.get_instance()

flask_api.ns('users').add_resource(RouteUsers, "/users")

flask_api.ns('stocks').add_resource(RouteStocks, "/stocks")
flask_api.ns('stock_prices').add_resource(RouteStockPrices, "/stock-prices")

flask_api.ns('investment-calculator').add_resource(RouteInvestmentCalculatorCompoundInterest,
                                                   "/investment-calculator/compound-interest")
flask_api.ns('investment-calculator').add_resource(RouteInvestmentCalculatorReturnRate,
                                                   "/investment-calculator/return-rate")
