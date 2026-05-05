from flask import Blueprint, request, jsonify, session
from models.trip import Trip
from models.booking import Booking
from models.user import User
from models.database import Database

customer_bp = Blueprint('customer', __name__, url_prefix='/api')

def filter_by_time(time_str, time_filter):
    """Filter trips by time of day"""
    hour = int(time_str.split(':')[0])
    if time_filter == 'morning':
        return 6 <= hour < 12
    elif time_filter == 'afternoon':
        return 12 <= hour < 17
    elif time_filter == 'evening':
        return 17 <= hour < 22
    return True

def filter_by_boat_type(boat_type_str, filter_type):
    """Filter by boat type"""
    boat_types = {
        'Sea Breeze 1': 'standard',
        'Ocean Voyager': 'fast',
        'Island Hopper': 'standard'
    }
    return boat_types.get(boat_type_str) == filter_type

@customer_bp.route('/trips', methods=['GET'])
def api_get_trips():
    from_port = request.args.get('from')
    to_port = request.args.get('to')
    date = request.args.get('date')
    
    # New filter parameters
    time_filter = request.args.get('time')  # morning, afternoon, evening
    boat_type = request.args.get('boat_type')  # standard, fast, luxury
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    trips = Trip.search(from_port, to_port, date)
    
    # Apply filters
    if time_filter:
        trips = [t for t in trips if filter_by_time(t['time'], time_filter)]
    
    if boat_type:
        trips = [t for t in trips if filter_by_boat_type(t.get('boat_name'), boat_type)]
    
    if min_price:
        trips = [t for t in trips if t['price'] >= min_price]
    
    if max_price:
        trips = [t for t in trips if t['price'] <= max_price]
    
    return jsonify(trips)

@customer_bp.route('/book', methods=['POST'])
def api_book_ticket():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    data = request.json
    trip_id = data.get('trip_id')
    passengers = data.get('passengers', 1)
    payment_method = data.get('payment_method', 'cash')
    
    # First, check availability without transaction (fast check)
    available, available_seats = Trip.check_availability(trip_id, passengers)
    if not available:
        return jsonify({'success': False, 'message': f'Sorry! Only {available_seats} seat(s) available'})
    
    # Get trip details
    trip = Trip.find_by_id(trip_id)
    if not trip:
        return jsonify({'success': False, 'message': 'Trip not found'})
    
    user = User.find_by_id(session['user_id'])
    total_amount = trip['price'] * passengers
    
    # Use transaction-enabled save
    booking = Booking(
        trip_id=trip_id,
        customer_id=user.id,
        customer_name=user.name,
        customer_email=user.email,
        passengers=passengers,
        total_amount=total_amount
    )
    
    # This uses transaction to prevent overbooking
    result = booking.save_with_transaction()
    
    # Log payment method (optional)
    if result['success']:
        # You can add payment record here
        pass
    
    return jsonify(result)

@customer_bp.route('/bookings', methods=['GET'])
def api_get_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    bookings = Booking.get_by_customer(session['user_id'])
    return jsonify(bookings)

@customer_bp.route('/stats', methods=['GET'])
def api_get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    stats = Booking.get_stats(session['user_id'])
    return jsonify(stats)

@customer_bp.route('/payments')
def api_get_payments():
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'})
        
        print(f"User ID: {session['user_id']}")
        
        from models.database import Database
        db = Database()
        db.connect()
        
        query = """
            SELECT t.from_port, t.to_port, t.departure_date, b.total_amount, b.status
            FROM bookings b
            JOIN trips t ON b.trip_id = t.id
            WHERE b.customer_id = %s
            ORDER BY t.departure_date DESC
        """
        
        results = db.execute_query(query, (session['user_id'],))
        db.disconnect()
        
        print(f"Results: {results}")
        
        if not results:
            return jsonify([])
        
        payments = []
        for row in results:
            payments.append({
                'route': f"{row[0]} → {row[1]}",
                'method': 'Cash',
                'date': str(row[2]),
                'amount': f"₱{float(row[3])}",
                'status': 'paid' if row[4] == 'confirmed' else 'pending'
            })
        
        return jsonify(payments)
        
    except Exception as e:
        print(f"Payment error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@customer_bp.route('/my-reservations')
def api_my_reservations():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    print(f"Fetching reservations for user: {session['user_id']}")  # Debug
    
    from models.database import Database
    db = Database()
    db.connect()
    
    results = db.execute_query("""
        SELECT b.booking_ref, t.from_port, t.to_port, t.departure_date, t.departure_time, 
               b.passengers, b.total_amount, b.status
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.customer_id = %s AND t.departure_date >= CURRENT_DATE
        ORDER BY t.departure_date ASC
    """, (session['user_id'],))
    
    db.disconnect()
    
    print(f"Found {len(results) if results else 0} reservations")  # Debug
    
    reservations = []
    if results:
        for row in results:
            reservations.append({
                'ref': row[0],
                'from': row[1],
                'to': row[2],
                'date': str(row[3]),
                'time': str(row[4]),
                'passengers': row[5],
                'amount': float(row[6]),
                'status': row[7]
            })
    
    return jsonify(reservations)

@customer_bp.route('/cancel-request', methods=['POST'])
def cancel_booking_request():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    data = request.json
    booking_ref = data.get('booking_ref')
    reason = data.get('reason')
    
    db = Database()
    db.connect()
    
    # Check if booking exists and belongs to user
    booking = db.execute_query("""
        SELECT id, status FROM bookings 
        WHERE booking_ref = %s AND customer_id = %s
    """, (booking_ref, session['user_id']))
    
    if not booking:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Booking not found'})
    
    # Update booking status to cancelled
    db.execute_insert("UPDATE bookings SET status = 'cancelled' WHERE booking_ref = %s", (booking_ref,))
    
    # Create notification for the user
    db.execute_insert("""
        INSERT INTO notifications (user_id, title, message, icon, color, bg)
        VALUES (%s, 'Booking Cancelled', %s, 'x-circle', '#ef4444', '#fef2f2')
    """, (session['user_id'], f'Your booking {booking_ref} has been cancelled.'))
    
    db.disconnect()
    
    return jsonify({'success': True, 'message': 'Booking cancelled successfully!'})