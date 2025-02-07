"""
Wrapper classes for flask.Flask and flask_restplus.Api
"""

import os

from flask import Flask
from flask_restplus import Api as RestPlusBaseApi
from flask_restplus import Resource


class FlaskApp:
    app_instance = None

    def __init__(self):
        raise Exception(
            "FlaskApp constructor called directly. Use get_instance() method."
        )

    @staticmethod
    def get_instance() -> Flask:
        if FlaskApp.app_instance is None:
            FlaskApp.app_instance = Flask(
                __name__, static_url_path="", static_folder=".", template_folder="."
            )
            FlaskApp.app_instance.url_map.strict_slashes = False
            FlaskApp.app_instance.config["SECRET_KEY"] = os.environ["FLASK_SECRET"]
            FlaskApp.app_instance.config[
                "SQLALCHEMY_DATABASE_URI"
            ] = f"sqlite://///usr/flask-app/data/users.sqlite"
            FlaskApp.app_instance.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        return FlaskApp.app_instance


class FlaskRestPlusApi(RestPlusBaseApi):
    api_instance = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ns_dict = {}

    @staticmethod
    def get_instance():
        if FlaskRestPlusApi.api_instance is None:
            FlaskRestPlusApi.api_instance = FlaskRestPlusApi(
                app=FlaskApp.get_instance(), version="0.0.1", prefix="/api/v1"
            )
        return FlaskRestPlusApi.api_instance

    def add_resource(self, cls: Resource, *args):
        self.default_namespace.add_resource(cls, *args)

    def ns(self, name: str, description=None, **kwargs):
        if name in self.ns_dict:
            return self.ns_dict[name]
        _ns = self.namespace(name, path="/", description=description, **kwargs)
        self.ns_dict[name] = _ns
        return _ns
