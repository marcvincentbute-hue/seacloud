from models.database import Database

class User:
    """User class for handling user operations"""
    
    def __init__(self, id=None, name=None, email=None, password=None, phone=None, role=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.phone = phone
        self.role = role or 'customer'
        self.db = Database()
    
    def save(self):
        """Save user to database (CREATE)"""
        try:
            self.db.connect()
            query = """
                INSERT INTO users (name, email, password, phone, role)
                VALUES (%s, %s, %s, %s, %s)
            """
            params = (self.name, self.email, self.password, self.phone, self.role)
            success = self.db.execute_insert(query, params)
            self.db.disconnect()
            
            if success:
                print(f"User saved: {self.email}")
            else:
                print(f"Failed to save user: {self.email}")
            return success
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def update(self):
        """Update user in database (UPDATE)"""
        self.db.connect()
        query = """
            UPDATE users 
            SET name = %s, phone = %s
            WHERE id = %s
        """
        params = (self.name, self.phone, self.id)
        success = self.db.execute_insert(query, params)
        self.db.disconnect()
        return success
    
    def delete(self):
        """Delete user from database (DELETE)"""
        self.db.connect()
        query = "DELETE FROM users WHERE id = %s"
        success = self.db.execute_insert(query, (self.id,))
        self.db.disconnect()
        return success
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find user by ID (READ)"""
        db = Database()
        db.connect()
        query = "SELECT id, name, email, phone, role FROM users WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        db.disconnect()
        
        if result:
            return cls(
                id=result[0][0],
                name=result[0][1],
                email=result[0][2],
                phone=result[0][3],
                role=result[0][4]
            )
        return None
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        db = Database()
        db.connect()
        query = "SELECT id, name, email, password, phone, role FROM users WHERE email = %s"
        result = db.execute_query(query, (email,))
        db.disconnect()
        
        if result:
            return cls(
                id=result[0][0],
                name=result[0][1],
                email=result[0][2],
                password=result[0][3],
                phone=result[0][4],
                role=result[0][5]
            )
        return None
    
    @classmethod
    def get_all(cls):
        """Get all users (READ)"""
        db = Database()
        db.connect()
        query = "SELECT id, name, email, phone, role FROM users"
        results = db.execute_query(query)
        db.disconnect()
        
        users = []
        for row in results:
            users.append(cls(
                id=row[0],
                name=row[1],
                email=row[2],
                phone=row[3],
                role=row[4]
            ))
        return users
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role
        }