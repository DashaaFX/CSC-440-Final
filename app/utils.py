from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Role

def paginate(query, page: int, per_page: int):
    """Simple manual pagination helper returning dict with items and metadata."""
    if page < 1:
        page = 1
    total = query.count()
    pages = (total + per_page - 1) // per_page if total else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages,
        'has_prev': page > 1,
        'has_next': page < pages
    }

def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            current_role_value = getattr(current_user.role, 'value', str(current_user.role))
            allowed_values = [r if isinstance(r, str) else getattr(r, 'value', str(r)) for r in roles]
            if current_role_value not in allowed_values:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def is_manager():
    return current_user.is_authenticated and getattr(current_user.role, 'value', str(current_user.role)) == Role.manager.value

def is_technician():
    return current_user.is_authenticated and getattr(current_user.role, 'value', str(current_user.role)) == Role.technician.value

def is_requester():
    return current_user.is_authenticated and getattr(current_user.role, 'value', str(current_user.role)) == Role.requester.value
