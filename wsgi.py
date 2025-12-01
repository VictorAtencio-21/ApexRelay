# wsgi.py
from f1_api import create_app

# Choose config here: "development", "production", "testing"
app = create_app("development")
