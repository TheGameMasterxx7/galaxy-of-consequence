import logging
from flask import request

VALID_BEARER_TOKEN = "Abracadabra"

def validate_bearer_token(request_obj):
    """
    Validate Bearer token from request headers
    Returns True if valid, False otherwise
    """
    try:
        auth_header = request_obj.headers.get('Authorization')
        
        if not auth_header:
            logging.warning("No Authorization header found")
            return False
        
        if not auth_header.startswith('Bearer '):
            logging.warning("Authorization header does not start with 'Bearer '")
            return False
        
        token = auth_header.split(' ')[1]
        
        if token != VALID_BEARER_TOKEN:
            logging.warning(f"Invalid bearer token: {token}")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"Error validating bearer token: {str(e)}")
        return False

def get_user_from_token(request_obj):
    """
    Extract user information from token (for this system, we'll use a default user)
    In a real system, this would decode JWT and extract user info
    """
    try:
        if validate_bearer_token(request_obj):
            # For this system, we'll return a default user since we're using a fixed token
            return "authorized_user"
        return None
        
    except Exception as e:
        logging.error(f"Error extracting user from token: {str(e)}")
        return None

def require_auth(f):
    """
    Decorator to require authentication for endpoints
    """
    def decorated_function(*args, **kwargs):
        if not validate_bearer_token(request):
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function
