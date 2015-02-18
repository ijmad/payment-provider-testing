from functools import wraps
from flask import session

class SessionException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return self.message

def session_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ref' not in session:
            raise SessionException("You already completed this payment")
        return f(*args, **kwargs)
    return decorated_function