from flask_sqlalchemy import SQLAlchemy


class SQLAlchemyDB:
    db_instance = None

    def __init__(self):
        raise Exception('FlaskApp constructor called directly. Use get_instance() method.')

    @staticmethod
    def get_instance() -> SQLAlchemy:
        if SQLAlchemyDB.db_instance is None:
            SQLAlchemyDB.db_instance = SQLAlchemy()

        return SQLAlchemyDB.db_instance


db = SQLAlchemyDB.get_instance()
