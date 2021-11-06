from webserver.flask_rest import FlaskApp, FlaskRestPlusApi
from webserver.routes.authentication import RouteLogin
from webserver.routes.investment_calculator import RouteInvestmentCalculatorCompoundInterest
from webserver.routes.portfolio import RoutePortfolio, RouteBacktest
from webserver.routes.stock_prices import RouteStockPrices
from webserver.routes.stocks import RouteStocks

# create flask app
from webserver.routes.users import RouteUsers

flask_app = FlaskApp.get_instance()
flask_api = FlaskRestPlusApi.get_instance()

authorizations = {
    'Basic Auth': {
        'type': 'basic',
        'in': 'header',
        'name': 'Authorization'
    },
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'x-access-token'
    }
}

flask_api.ns('auth', security='Basic Auth', authorizations=authorizations).add_resource(RouteLogin, "/login")

flask_api.ns('users', security='apiKey', authorizations=authorizations).add_resource(RouteUsers, "/users")

flask_api.ns('stocks', security='apiKey', authorizations=authorizations).add_resource(RouteStocks, "/stocks")
flask_api.ns('stock-prices', security='apiKey', authorizations=authorizations).add_resource(RouteStockPrices,
                                                                                            "/stock-prices")

flask_api.ns('portfolio', security='apiKey', authorizations=authorizations).add_resource(RoutePortfolio,
                                                                                         "/portfolio")
flask_api.ns('portfolio', security='apiKey', authorizations=authorizations).add_resource(RouteBacktest,
                                                                                         "/portfolio/backtest")

flask_api.ns('investment-calculator').add_resource(RouteInvestmentCalculatorCompoundInterest,
                                                   "/investment-calculator/compound-interest")
