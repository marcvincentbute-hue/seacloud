import os
from urllib.parse import urlparse

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Production (Render)
        url = urlparse(DATABASE_URL)
        DB_HOST = url.hostname
        DB_NAME = url.path[1:]
        DB_USER = url.username
        DB_PASSWORD = url.password
        DB_PORT = url.port or 5432
    else:
        # Local development
        DB_HOST = "localhost"
        DB_NAME = "seacloud_db"
        DB_USER = "postgres"
        DB_PASSWORD = "admin123"
        DB_PORT = "5433"
    
    SECRET_KEY = "seacloud123"