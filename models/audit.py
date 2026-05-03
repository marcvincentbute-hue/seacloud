from models.database import Database
from flask import request

class AuditLog:
    @staticmethod
    def log(user_id, user_name, action, table_name=None, record_id=None, old_data=None, new_data=None):
        db = Database()
        db.connect()
        
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        query = """
            INSERT INTO audit_logs (user_id, user_name, action, table_name, record_id, old_data, new_data, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        db.execute_insert(query, (user_id, user_name, action, table_name, record_id, old_data, new_data, ip_address))
        db.disconnect()