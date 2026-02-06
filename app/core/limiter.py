from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

def user_or_ip_key(request: Request):
    # Try to read user_id set by auth dependency
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id

    # Fallback to IP (for unauth endpoints like /health)
    return request.client.host

limiter = Limiter(key_func=user_or_ip_key)
