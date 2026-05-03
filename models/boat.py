from models.database import Database

class Boat:
    """Boat class for managing ferry boats"""
    
    def __init__(self, id=None, name=None, capacity=None, operator_id=None, status='available'):
        self.id = id
        self.name = name
        self.capacity = capacity
        self.operator_id = operator_id
        self.status = status
        self.db = Database()
    
    def save(self):
        """Save boat to database (CREATE)"""
        self.db.connect()
        query = """
            INSERT INTO boats (name, capacity, operator_id, status)
            VALUES (%s, %s, %s, %s)
        """
        params = (self.name, self.capacity, self.operator_id, self.status)
        success = self.db.execute_insert(query, params)
        
        if success:
            self.id = self.db.get_last_id()
        self.db.disconnect()
        return success
    
    def update(self):
        """Update boat (UPDATE)"""
        self.db.connect()
        query = """
            UPDATE boats 
            SET name = %s, capacity = %s, status = %s
            WHERE id = %s
        """
        params = (self.name, self.capacity, self.status, self.id)
        success = self.db.execute_insert(query, params)
        self.db.disconnect()
        return success
    
    def delete(self):
        """Delete boat (DELETE)"""
        self.db.connect()
        query = "DELETE FROM boats WHERE id = %s"
        success = self.db.execute_insert(query, (self.id,))
        self.db.disconnect()
        return success
    
    @classmethod
    def find_by_id(cls, boat_id):
        """Find boat by ID (READ)"""
        db = Database()
        db.connect()
        query = "SELECT id, name, capacity, operator_id, status FROM boats WHERE id = %s"
        result = db.execute_query(query, (boat_id,))
        db.disconnect()
        
        if result:
            return cls(
                id=result[0][0],
                name=result[0][1],
                capacity=result[0][2],
                operator_id=result[0][3],
                status=result[0][4]
            )
        return None
    
    @classmethod
    def get_by_operator(cls, operator_id):
        """Get all boats by operator"""
        db = Database()
        db.connect()
        query = "SELECT id, name, capacity, status FROM boats WHERE operator_id = %s"
        results = db.execute_query(query, (operator_id,))
        db.disconnect()
        
        boats = []
        for row in results:
            boats.append(cls(
                id=row[0],
                name=row[1],
                capacity=row[2],
                status=row[3]
            ))
        return boats
    
    @classmethod
    def get_all_available(cls):
        """Get all available boats"""
        db = Database()
        db.connect()
        query = "SELECT id, name, capacity FROM boats WHERE status = 'available'"
        results = db.execute_query(query)
        db.disconnect()
        
        boats = []
        for row in results:
            boats.append(cls(
                id=row[0],
                name=row[1],
                capacity=row[2]
            ))
        return boats
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'status': self.status
        }