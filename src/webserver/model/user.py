"""
Flask-SQLAlchmey model classes.
"""

from webserver.model.db import db


# noinspection PyUnresolvedReferences
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    admin = db.Column(db.Boolean)
