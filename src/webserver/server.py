from webserver.flask_rest import FlaskApp, FlaskRestPlusApi
from webserver.routes.api_routes import RouteStocks, RouteStockPrices

flask_app = FlaskApp.get_instance()
flask_api = FlaskRestPlusApi.get_instance()

flask_api.ns('stocks').add_resource(RouteStocks, "/stocks")
flask_api.ns('stock_prices').add_resource(RouteStockPrices, "/stock-prices")
