import uuid

from sqlalchemy.exc import IntegrityError

from webserver.decorators import fails_safe_request
from webserver.models.db import db
from webserver.models.user import User


class UsersManagementAPI:

    @staticmethod
    @fails_safe_request
    def get_users(public_id=None) -> tuple:
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
    @fails_safe_request
    def create_user(username, hashed_password) -> tuple:
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
    @fails_safe_request
    def promote_user(public_id) -> tuple:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return 404, {}, 'User not found.'
        user.admin = True
        db.session.commit()
        return 200, {'message': 'User {} promoted'.format(public_id)}, 'OK'

    @staticmethod
    @fails_safe_request
    def delete_use(public_id) -> tuple:
        user = User.query.filter_by(public_id=public_id).first()
        if not user:
            return 404, {}, 'User not found.'
        db.session.delete(user)
        db.session.commit()
        return 200, {'message': 'User {} deleted.'.format(public_id)}, 'OK'
