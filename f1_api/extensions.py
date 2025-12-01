# f1_api/extensions.py
from flask_cors import CORS
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# These are "unbound" instances; we bind them to the app in create_app()
cors = CORS()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address, 
    default_limits=["60 per minute"],
)
