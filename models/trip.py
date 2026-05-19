from models.database import Database
from datetime import datetime

class Trip:
    def __init__(self, id=None, boat_id=None, origin=None, destination=None, 
                 departure_date=None, departure_time=None, price=None, operator_id=None):
        self.id = id
        self.boat_id = boat_id
        self.origin = origin           
        self.destination = destination 
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.price = price
        self.operator_id = operator_id
        self.status = 'scheduled'
        self.db = Database()
    
    def save(self):
        query = """
            INSERT INTO trips (boat_id, origin, destination, departure_date, 
                               departure_time, price, operator_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.boat_id, self.origin, self.destination, self.departure_date,
                  self.departure_time, self.price, self.operator_id, self.status)
        success = self.db.execute_insert(query, params)
        
        if success:
            self.id = self.db.get_last_id()
        self.db.disconnect()
        return success
    
    def update(self):
        """Update trip (UPDATE)"""
        self.db.connect()
        query = """
            UPDATE trips 
            SET from_port = %s, to_port = %s, departure_date = %s, 
                departure_time = %s, price = %s, status = %s
            WHERE id = %s
        """
        params = (self.from_port, self.to_port, self.departure_date,
                  self.departure_time, self.price, self.status, self.id)
        success = self.db.execute_insert(query, params)
        self.db.disconnect()
        return success
    
    def delete(self):
        """Delete trip (DELETE)"""
        self.db.connect()
        query = "DELETE FROM trips WHERE id = %s"
        success = self.db.execute_insert(query, (self.id,))
        self.db.disconnect()
        return success
    
    @classmethod
    def find_by_id(cls, trip_id):
        """Find trip by ID (READ)"""
        db = Database()
        db.connect()
        query = """
            SELECT t.id, t.from_port, t.to_port, t.departure_date, 
                   t.departure_time, t.price, b.name as boat_name
            FROM trips t
            JOIN boats b ON t.boat_id = b.id
            WHERE t.id = %s
        """
        result = db.execute_query(query, (trip_id,))
        db.disconnect()
        
        if result:
            return {
                'id': result[0][0],
                'from': result[0][1],
                'to': result[0][2],
                'date': str(result[0][3]),
                'time': str(result[0][4]),
                'price': float(result[0][5]),
                'boat': result[0][6]
            }
        return None
    
    @classmethod
    def search(cls, from_port, to_port, date):
        """Search for available trips (READ)"""
        db = Database()
        db.connect()
        query = """
            SELECT t.id, t.from_port, t.to_port, t.departure_date, 
                   t.departure_time, t.price, b.name as boat_name, b.capacity,
                   t.available_seats
            FROM trips t
            JOIN boats b ON t.boat_id = b.id
            WHERE t.from_port = %s 
              AND t.to_port = %s 
              AND t.departure_date = %s
              AND t.status = 'scheduled'
            ORDER BY t.departure_time
        """
        results = db.execute_query(query, (from_port, to_port, date))
        db.disconnect()
        
        trips = []
        for row in results:
            trips.append({
                'id': row[0],
                'from_port': row[1],
                'to_port': row[2],
                'date': str(row[3]),
                'time': str(row[4]),
                'price': float(row[5]),
                'boat_name': row[6],
                'capacity': row[7],
                'available_seats': row[8]
            })
        return trips
    
    def to_dict(self):
        return {
            'id': self.id,
            'from': self.from_port,
            'to': self.to_port,
            'date': str(self.departure_date),
            'time': str(self.departure_time),
            'price': float(self.price)
        }
    
    @classmethod
    def check_availability(cls, trip_id, requested_passengers):
        """Check if trip has enough available seats using available_seats field"""
        db = Database()
        db.connect()
        
        db.cursor.execute(
            "SELECT available_seats FROM trips WHERE id = %s",
            (trip_id,)
        )
        
        result = db.cursor.fetchone()
        db.disconnect()
        
        if result:
            available = result[0]
            return available >= requested_passengers, available
        
        return False, 0