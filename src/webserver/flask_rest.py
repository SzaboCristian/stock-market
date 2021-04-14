"""
Wrapper classes for flask.Flask and flask_restplus.Api
"""

__version__ = "0.0.1"
__author__ = "Szabo Cristian"

from flask import Flask
from flask_restplus import Api as RestPlusBaseApi, Resource


class FlaskApp:
    app_instance = None

    def __init__(self):
        app = Flask(__name__,
                    static_url_path="",
                    static_folder=".",
                    template_folder=".")
        app.url_map.strict_slashes = False

    @staticmethod
    def get_instance() -> Flask:
        if FlaskApp.app_instance is None:
            FlaskApp.app_instance = Flask(__name__,
                                          static_url_path="",
                                          static_folder=".",
                                          template_folder=".")
            FlaskApp.app_instance.url_map.strict_slashes = False

        return FlaskApp.app_instance


class FlaskRestPlusApi(RestPlusBaseApi):
    api_instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ns_dict = {}

    @staticmethod
    def get_instance():
        if FlaskRestPlusApi.api_instance is None:
            FlaskRestPlusApi.api_instance = FlaskRestPlusApi(app=FlaskApp.get_instance())
        return FlaskRestPlusApi.api_instance

    def add_resource(self, cls: Resource, *args):
        self.default_namespace.add_resource(cls, *args)

    def ns(self, name: str, description=None):
        if name in self.ns_dict:
            return self.ns_dict[name]
        _ns = self.namespace(name, path="/", description=description)
        self.ns_dict[name] = _ns
        return _ns
