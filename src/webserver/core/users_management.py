import uuid

from sqlalchemy.exc import IntegrityError

from webserver.models.db import db
from webserver.models.user import User


class UsersManagementAPI:

    @staticmethod
    def get_users(public_id=None):
        if not public_id:
            users = User.query.all()
            users = [{'public_id': user.public_id, 'username': user.username, 'password': user.password,
                      'admin': bool(user.admin)} for user in users]
            if users:
                return 200, users, 'OK'
        else:
            user = User.query.filter_by(public_id=public_id).first()
            if user:
                return 200, {'public_id': user.public_id, 'username': user.username, 'password': user.password,
                             'admin': bool(user.admin)}, 'OK'

        return 404, {}, 'User not found.'

    @staticmethod
    def create_user(username, hashed_password):
        try:
            new_user = User(public_id=str(uuid.uuid4()), username=username, password=hashed_password, admin=False)
            db.session.add(new_user)
            db.session.commit()
            return 201, {'message': 'New user created!'}, 'OK'
        except IntegrityError as e:
            if 'UNIQUE constraint failed: user.username' in str(e):
                return 409, {}, "Username already exists."
            return 500, {}, 'Could not create user.'

    @staticmethod
    def promote_user(public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return 404, {}, 'User not found.'
        user.admin = True
        db.session.commit()
        return 200, {'message': 'User {} promoted'.format(public_id)}, 'OK'

    @staticmethod
    def delete_use(public_id):
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return 404, {}, 'User not found.'
        db.session.delete(user)
        db.session.commit()
        return 200, {'message': 'User {} deleted.'.format(public_id)}, 'OK'
