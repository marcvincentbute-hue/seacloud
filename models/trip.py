from models.database import Database
from datetime import datetime

class Trip:
    """Trip/Schedule class for managing ferry trips"""
    
    def __init__(self, id=None, boat_id=None, from_port=None, to_port=None, 
                 departure_date=None, departure_time=None, price=None, operator_id=None):
        self.id = id
        self.boat_id = boat_id
        self.from_port = from_port
        self.to_port = to_port
        self.departure_date = departure_date
        self.departure_time = departure_time
        self.price = price
        self.operator_id = operator_id
        self.status = 'scheduled'
        self.db = Database()
    
    def save(self):
        """Save trip to database (CREATE)"""
        self.db.connect()
        query = """
            INSERT INTO trips (boat_id, from_port, to_port, departure_date, 
                               departure_time, price, operator_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.boat_id, self.from_port, self.to_port, self.departure_date,
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
                   t.departure_time, t.price, b.name as boat_name, b.capacity
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
                'capacity': row[7]
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
    def generate_seats(cls, trip_id, capacity):
        """Generate seats for a trip (e.g., A1, A2, B1, B2...)"""
        db = Database()
        db.connect()
    
        seats = []
        rows = ['A', 'B', 'C', 'D', 'E', 'F']
        seats_per_row = 4
    
        seat_count = 0
        for row in rows:
            for num in range(1, seats_per_row + 1):
                if seat_count >= capacity:
                    break
                seat_number = f"{row}{num}"
                seats.append((trip_id, seat_number))
                seat_count += 1
            if seat_count >= capacity:
                break
    
        query = "INSERT INTO trip_seats (trip_id, seat_number) VALUES (%s, %s)"
        for seat in seats:
            db.execute_insert(query, seat)
    
        db.disconnect()
        return len(seats)

    @classmethod
    def get_available_seats(cls, trip_id):
        """Get available seats for a trip"""
        db = Database()
        db.connect()
        results = db.execute_query(
            "SELECT seat_number FROM trip_seats WHERE trip_id = %s AND is_booked = FALSE",
            (trip_id,)
        )
        db.disconnect()
        return [row[0] for row in results] if results else []

    @classmethod
    def book_seat(cls, trip_id, seat_number, booking_id):
        """Book a specific seat"""
        db = Database()
        db.connect()
        success = db.execute_insert(
            "UPDATE trip_seats SET is_booked = TRUE, booking_id = %s WHERE trip_id = %s AND seat_number = %s AND is_booked = FALSE",
            (booking_id, trip_id, seat_number)
        )
        db.disconnect()
        return success
    
    @classmethod
    def check_availability(cls, trip_id, requested_passengers):
        """Check if trip has enough available seats"""
        db = Database()
        db.connect()
        
        # Get boat capacity
        db.cursor.execute("""
            SELECT b.capacity, COALESCE(SUM(bk.passengers), 0)
            FROM boats b
            JOIN trips t ON b.id = t.boat_id
            LEFT JOIN bookings bk ON t.id = bk.trip_id AND bk.status = 'confirmed'
            WHERE t.id = %s
            GROUP BY b.capacity
        """, (trip_id,))
        
        result = db.cursor.fetchone()
        db.disconnect()
        
        if result:
            capacity = result[0]
            booked = result[1] or 0
            available = capacity - booked
            return available >= requested_passengers, available
        
        return False, 0