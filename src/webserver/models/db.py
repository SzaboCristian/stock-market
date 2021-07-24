from flask_sqlalchemy import SQLAlchemy

# TODO - make singleton db = DB.get_instance() and return that way so we won't have many connections
db = SQLAlchemy()
