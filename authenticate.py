from functools import wraps
from flask import request, Response


def basicauth(username, password):
    # this screams for MIM attacks. Set up your SSL connection.
    def outer(f):
        @wraps(f)
        def decorate(*args, **kwargs):
            if request.authorization \
                    and (request.authorization.username, request.authorization.password) == (username, password):
                    # bogus decorator credential check, replace with db call
                return f(*args, **kwargs)
            else:
                return Response('Could not verify your access level for that URL.\n'
                                'You have to login with proper credentials', 401,
                                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return decorate
    return outer
