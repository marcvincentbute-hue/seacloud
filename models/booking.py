from models.database import Database
import uuid

class Booking:
    """Booking class for managing ticket bookings"""
    
    def __init__(self, id=None, booking_ref=None, trip_id=None, customer_id=None,
                 customer_name=None, customer_email=None, passengers=1, total_amount=None):
        self.id = id
        self.booking_ref = booking_ref or str(uuid.uuid4())[:8].upper()
        self.trip_id = trip_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.customer_email = customer_email
        self.passengers = passengers
        self.total_amount = total_amount
        self.status = 'confirmed'
        self.db = Database()
    
    def save_with_transaction(self):
        """Save booking using database transaction (prevents overbooking)"""
        self.db.connect()
        
        try:
            # Start transaction
            self.db.connection.autocommit = False
            
            # Lock the trip row to prevent concurrent bookings
            self.db.cursor.execute("SELECT capacity FROM boats b JOIN trips t ON b.id = t.boat_id WHERE t.id = %s FOR UPDATE", (self.trip_id,))
            boat_capacity = self.db.cursor.fetchone()
            
            if not boat_capacity:
                raise Exception("Trip not found")
            
            # Check current total passengers
            self.db.cursor.execute("""
                SELECT COALESCE(SUM(passengers), 0) FROM bookings 
                WHERE trip_id = %s AND status = 'confirmed'
                FOR UPDATE
            """, (self.trip_id,))
            current_booked = self.db.cursor.fetchone()[0]
            
            # Check if still available
            available_seats = boat_capacity[0] - current_booked
            
            if available_seats < self.passengers:
                self.db.connection.rollback()
                self.db.disconnect()
                return {'success': False, 'message': f'Only {available_seats} seat(s) available'}
            
            # Insert booking
            query = """
                INSERT INTO bookings (booking_ref, trip_id, customer_id, customer_name,
                                       customer_email, passengers, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (self.booking_ref, self.trip_id, self.customer_id, 
                      self.customer_name, self.customer_email, 
                      self.passengers, self.total_amount, self.status)
            
            self.db.cursor.execute(query, params)
            
            # Commit transaction
            self.db.connection.commit()
            self.db.disconnect()
            
            return {'success': True, 'message': 'Booking confirmed!', 'ref': self.booking_ref}
            
        except Exception as e:
            self.db.connection.rollback()
            self.db.disconnect()
            print(f"Transaction error: {e}")
            return {'success': False, 'message': str(e)}
    
    def save(self):
        """Original save method (without transaction - for reference)"""
        self.db.connect()
        query = """
            INSERT INTO bookings (booking_ref, trip_id, customer_id, customer_name,
                                   customer_email, passengers, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (self.booking_ref, self.trip_id, self.customer_id, 
                  self.customer_name, self.customer_email, 
                  self.passengers, self.total_amount, self.status)
        success = self.db.execute_insert(query, params)
        
        if success:
            self.id = self.db.get_last_id()
        self.db.disconnect()
        return success
    
    
    def cancel(self):
        """Cancel booking (UPDATE - status to cancelled)"""
        self.db.connect()
        query = "UPDATE bookings SET status = 'cancelled' WHERE id = %s"
        success = self.db.execute_insert(query, (self.id,))
        self.db.disconnect()
        
        if success:
            self.status = 'cancelled'
        return success
    
    @classmethod
    def get_by_customer(cls, customer_id):
        """Get all bookings by customer (READ)"""
        db = Database()
        db.connect()
        query = """
            SELECT b.booking_ref, b.passengers, b.total_amount, b.status, b.booking_date,
                   t.from_port, t.to_port, t.departure_date
            FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s
            ORDER BY b.booking_date DESC
        """
        results = db.execute_query(query, (customer_id,))
        db.disconnect()
        
        bookings = []
        for row in results:
            bookings.append({
                'ref': row[0],
                'passengers': row[1],
                'amount': float(row[2]),
                'status': row[3],
                'date': str(row[4]),
                'from': row[5],
                'to': row[6],
                'departure_date': str(row[7])
            })
        return bookings
    
    @classmethod
    def get_stats(cls, customer_id):
        """Get booking statistics for customer"""
        db = Database()
        db.connect()
        
        # Total bookings
        query1 = "SELECT COUNT(*) FROM bookings WHERE customer_id = %s"
        total = db.execute_query(query1, (customer_id,))[0][0]
        
        # Upcoming trips
        query2 = """
            SELECT COUNT(*) FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s AND t.departure_date >= CURRENT_DATE
        """
        upcoming = db.execute_query(query2, (customer_id,))[0][0]
        
        # Completed trips
        query3 = """
            SELECT COUNT(*) FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s AND t.departure_date < CURRENT_DATE
        """
        completed = db.execute_query(query3, (customer_id,))[0][0]
        
        db.disconnect()
        
        return {
            'total': total,
            'upcoming': upcoming,
            'completed': completed
        }
    
    def to_dict(self):
        return {
            'ref': self.booking_ref,
            'passengers': self.passengers,
            'amount': float(self.total_amount),
            'status': self.status
        }