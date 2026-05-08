from config import Config
import psycopg2
from psycopg2 import OperationalError

class Database:
    """Database connection manager class"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        try:
            # Use Config for database settings
            self.connection = psycopg2.connect(
                host=Config.DB_HOST,
                database=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                port=Config.DB_PORT
            )
            self.cursor = self.connection.cursor()
            print(f"✅ Database connected to {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
            return True
        except OperationalError as e:
            print(f"❌ Database connection error: {e}")
            return False
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("✅ Database disconnected!")
    
    def execute_query(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return self.cursor.fetchall()
            return True
        except Exception as e:
            print(f"Query error: {e}")
            return None
    
    def execute_insert(self, query, params=None):
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return True
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            print(f"Insert error: {e}")
            return False
    
    def get_last_id(self):
        self.cursor.execute("SELECT LASTVAL()")
        return self.cursor.fetchone()[0]