from webserver.flask_rest import FlaskApp, FlaskRestPlusApi
from webserver.routes.authentication import RouteLogin, RouteRegister
from webserver.routes.investment_calculator import RouteInvestmentCalculatorCompoundInterest
from webserver.routes.portofolios import RoutePortofolio, RouteBacktest
from webserver.routes.stock_prices import RouteStockPrices
from webserver.routes.stocks import RouteStocks
from webserver.routes.users import RouteUsers

# create flask app
flask_app = FlaskApp.get_instance()
flask_api = FlaskRestPlusApi.get_instance()

flask_api.ns('users').add_resource(RouteUsers, "/users")

flask_api.ns('auth').add_resource(RouteLogin, "/login")
flask_api.ns('auth').add_resource(RouteRegister, "/register")

flask_api.ns('stocks').add_resource(RouteStocks, "/stocks")
flask_api.ns('stock_prices').add_resource(RouteStockPrices, "/stock-prices")

flask_api.ns('portofolio').add_resource(RoutePortofolio, "/portofolio")
flask_api.ns('portofolio').add_resource(RouteBacktest, "/portofolio/backtest")

flask_api.ns('investment-calculator').add_resource(RouteInvestmentCalculatorCompoundInterest,
                                                   "/investment-calculator/compound-interest")
