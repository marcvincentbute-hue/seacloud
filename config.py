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
        print(f"✅ Using Render DB: {DB_HOST}")
    else:
        # Local development
        DB_HOST = "localhost"
        DB_NAME = "seacloud_db"
        DB_USER = "postgres"
        DB_PASSWORD = "admin123"
        DB_PORT = "5433"
        print("⚠️ Using local database")
    
    SECRET_KEY = "seacloud123"