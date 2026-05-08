from models.database import Database
import uuid

class Booking:
    """Booking class for managing ticket bookings"""
    
    def __init__(self, id=None, booking_ref=None, trip_id=None, customer_id=None,
                 passengers=1, total_amount=None):
        self.id = id
        self.booking_ref = booking_ref or str(uuid.uuid4())[:8].upper()
        self.trip_id = trip_id
        self.customer_id = customer_id
        self.passengers = passengers
        self.total_amount = total_amount
        self.status = 'confirmed'
        self.db = Database()
    
    def save_with_transaction(self):
        """Save booking using database transaction (prevents overbooking)"""
        self.db.connect()
        
        try:
            self.db.connection.autocommit = False
            
            # Use available_seats from trips table directly
            self.db.cursor.execute(
                "SELECT available_seats FROM trips WHERE id = %s FOR UPDATE", 
                (self.trip_id,)
            )
            result = self.db.cursor.fetchone()
            
            if not result:
                raise Exception("Trip not found")
            
            available_seats = result[0]
            
            if available_seats < self.passengers:
                self.db.connection.rollback()
                self.db.disconnect()
                return {'success': False, 'message': f'Only {available_seats} seat(s) available'}
            
            # Update available seats
            self.db.cursor.execute(
                "UPDATE trips SET available_seats = available_seats - %s WHERE id = %s",
                (self.passengers, self.trip_id)
            )
            
            # Insert booking (NO customer_name/email)
            query = """
                INSERT INTO bookings (booking_ref, trip_id, customer_id, passengers, total_amount, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (self.booking_ref, self.trip_id, self.customer_id, 
                      self.passengers, self.total_amount, self.status)
            
            self.db.cursor.execute(query, params)
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
            INSERT INTO bookings (booking_ref, trip_id, customer_id, passengers, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (self.booking_ref, self.trip_id, self.customer_id, 
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
            # Also add back the seats to available_seats
            db2 = Database()
            db2.connect()
            db2.execute_insert(
                "UPDATE trips SET available_seats = available_seats + %s WHERE id = %s",
                (self.passengers, self.trip_id)
            )
            db2.disconnect()
            self.status = 'cancelled'
        return success
    
    @classmethod
    def get_by_customer(cls, customer_id):
        """Get all bookings by customer (READ)"""
        db = Database()
        db.connect()
        
        query = """
            SELECT b.booking_ref, b.passengers, b.total_amount, b.status, b.booking_date,
                t.from_port, t.to_port, t.departure_date, t.departure_time
            FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s
            ORDER BY b.booking_date DESC
        """
        
        results = db.execute_query(query, (customer_id,))
        db.disconnect()
        
        if not results:
            return []
        
        bookings = []
        for row in results:
            # Format date nicely
            travel_date = row[7]  # departure_date
            travel_time = row[8]  # departure_time
            
            # Format date to YYYY-MM-DD only
            if travel_date:
                travel_date_str = str(travel_date).split(' ')[0]
            else:
                travel_date_str = 'N/A'
            
            # Format time to HH:MM only
            if travel_time:
                travel_time_str = str(travel_time).split('.')[0][:5]
            else:
                travel_time_str = 'N/A'
            
            bookings.append({
                'ref': row[0],
                'passengers': row[1],
                'amount': float(row[2]),
                'status': row[3],
                'date': travel_date_str,        # ← travel date, hindi booking date!
                'time': travel_time_str,        # ← formatted time
                'from': row[5],
                'to': row[6],
                'departure_date': travel_date_str,
                'booking_date': str(row[4]).split(' ')[0] if row[4] else 'N/A'
            })
        
        return bookings 
    
    @classmethod
    def get_stats(cls, customer_id):
        """Get booking statistics for customer"""
        db = Database()
        db.connect()
        
        query1 = "SELECT COUNT(*) FROM bookings WHERE customer_id = %s"
        total = db.execute_query(query1, (customer_id,))[0][0]
        
        query2 = """
            SELECT COUNT(*) FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s AND t.departure_date >= CURRENT_DATE
        """
        upcoming = db.execute_query(query2, (customer_id,))[0][0]
        
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