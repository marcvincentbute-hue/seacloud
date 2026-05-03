class Config:
    """Configuration class for the application"""
    
    # Database configuration
    DB_HOST = "localhost"
    DB_NAME = "seacloud_db"
    DB_USER = "postgres"
    DB_PASSWORD = "admin123"  
    DB_PORT = "5433"
    
    # Flask configuration
    SECRET_KEY = "seacloud123"