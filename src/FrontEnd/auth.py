from functools import wraps
from flask import session, redirect, url_for, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('frontend.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def is_authenticated():
    return 'user_id' in session

def get_current_user():
    if is_authenticated():
        return {
            'id': session.get('user_id'),
            'username': session.get('username'),
            'email': session.get('email')
        }
    return None

