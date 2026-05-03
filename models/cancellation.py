from models.database import Database
from datetime import datetime

class Cancellation:
    """Cancellation and Refund management"""
    
    def __init__(self, id=None, booking_id=None, booking_ref=None, customer_id=None, 
                 reason=None, refund_amount=None):
        self.id = id
        self.booking_id = booking_id
        self.booking_ref = booking_ref
        self.customer_id = customer_id
        self.reason = reason
        self.refund_amount = refund_amount
        self.status = 'pending'
        self.db = Database()
    
    def save(self):
        """Save cancellation request"""
        self.db.connect()
        query = """
            INSERT INTO cancellations (booking_id, booking_ref, customer_id, reason, refund_amount)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (self.booking_id, self.booking_ref, self.customer_id, self.reason, self.refund_amount)
        success = self.db.execute_insert(query, params)
        
        if success:
            self.id = self.db.get_last_id()
        self.db.disconnect()
        return success
    
    @classmethod
    def get_by_customer(cls, customer_id):
        """Get all cancellation requests by customer"""
        db = Database()
        db.connect()
        results = db.execute_query("""
            SELECT c.id, c.booking_ref, c.reason, c.status, c.refund_amount, 
                   c.requested_at, c.processed_at
            FROM cancellations c
            WHERE c.customer_id = %s
            ORDER BY c.requested_at DESC
        """, (customer_id,))
        db.disconnect()
        
        cancellations = []
        for row in results:
            cancellations.append({
                'id': row[0],
                'ref': row[1],
                'reason': row[2],
                'status': row[3],
                'refund_amount': float(row[4]) if row[4] else 0,
                'requested_at': str(row[5]),
                'processed_at': str(row[6]) if row[6] else None
            })
        return cancellations
    
    @classmethod
    def approve(cls, cancel_id, admin_id, refund_amount):
        """Approve cancellation request"""
        db = Database()
        db.connect()
        success = db.execute_insert("""
            UPDATE cancellations 
            SET status = 'approved', refund_amount = %s, processed_at = %s, processed_by = %s
            WHERE id = %s
        """, (refund_amount, datetime.now(), admin_id, cancel_id))
        db.disconnect()
        return success
    
    @classmethod
    def reject(cls, cancel_id, admin_id):
        """Reject cancellation request"""
        db = Database()
        db.connect()
        success = db.execute_insert("""
            UPDATE cancellations 
            SET status = 'rejected', processed_at = %s, processed_by = %s
            WHERE id = %s
        """, (datetime.now(), admin_id, cancel_id))
        db.disconnect()
        return success

class TripCancellation:
    """Trip cancellation management"""
    
    @classmethod
    def cancel_trip(cls, trip_id, operator_id, reason):
        """Cancel a trip and notify all affected passengers"""
        db = Database()
        db.connect()
        
        # Start transaction
        db.connection.autocommit = False
        
        try:
            # Record trip cancellation
            db.execute_insert("""
                INSERT INTO trip_cancellations (trip_id, reason, cancelled_by)
                VALUES (%s, %s, %s)
            """, (trip_id, reason, operator_id))
            
            # Update trip status
            db.execute_insert("UPDATE trips SET status = 'cancelled' WHERE id = %s", (trip_id,))
            
            # Get all affected bookings
            bookings = db.execute_query("""
                SELECT b.id, b.booking_ref, b.customer_id, b.customer_name, b.customer_email, 
                       b.total_amount, u.phone
                FROM bookings b
                JOIN users u ON b.customer_id = u.id
                WHERE b.trip_id = %s AND b.status = 'confirmed'
            """, (trip_id,))
            
            # Update booking status to cancelled
            for booking in bookings:
                db.execute_insert("""
                    UPDATE bookings SET status = 'cancelled' WHERE id = %s
                """, (booking[0],))
                
                # Auto-create cancellation record with full refund
                db.execute_insert("""
                    INSERT INTO cancellations (booking_id, booking_ref, customer_id, reason, 
                                               status, refund_amount, processed_at)
                    VALUES (%s, %s, %s, 'Trip cancelled by operator', 'approved', %s, %s)
                """, (booking[0], booking[1], booking[2], booking[4], datetime.now()))
            
            db.connection.commit()
            db.disconnect()
            
            return {'success': True, 'bookings': len(bookings), 'bookings_data': bookings}
            
        except Exception as e:
            db.connection.rollback()
            db.disconnect()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_cancelled_trips(cls):
        """Get all cancelled trips"""
        db = Database()
        db.connect()
        results = db.execute_query("""
            SELECT tc.id, t.id as trip_id, t.from_port, t.to_port, t.departure_date,
                   tc.reason, tc.cancelled_at, u.name as cancelled_by
            FROM trip_cancellations tc
            JOIN trips t ON tc.trip_id = t.id
            JOIN users u ON tc.cancelled_by = u.id
            ORDER BY tc.cancelled_at DESC
        """)
        db.disconnect()
        
        trips = []
        for row in results:
            trips.append({
                'id': row[0],
                'trip_id': row[1],
                'from': row[2],
                'to': row[3],
                'date': str(row[4]),
                'reason': row[5],
                'cancelled_at': str(row[6]),
                'cancelled_by': row[7]
            })
        return trips