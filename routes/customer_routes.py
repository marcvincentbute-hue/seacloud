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
    
    time_filter = request.args.get('time')
    boat_type = request.args.get('boat_type')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    trips = Trip.search(from_port, to_port, date)
    
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
    
    available, available_seats = Trip.check_availability(trip_id, passengers)
    if not available:
        return jsonify({'success': False, 'message': f'Sorry! Only {available_seats} seat(s) available'})
    
    trip = Trip.find_by_id(trip_id)
    if not trip:
        return jsonify({'success': False, 'message': 'Trip not found'})
    
    user = User.find_by_id(session['user_id'])
    total_amount = trip['price'] * passengers
    
    booking = Booking(
        trip_id=trip_id,
        customer_id=user.id,
        passengers=passengers,
        total_amount=total_amount
    )
    
    result = booking.save_with_transaction()
    
    return jsonify(result)

@customer_bp.route('/bookings', methods=['GET'])
def api_get_bookings():
    """Get all bookings for the logged-in customer"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    print(f"📖 Fetching bookings for user_id: {session['user_id']}")
    
    bookings = Booking.get_by_customer(session['user_id'])
    
    print(f"📦 Found {len(bookings)} bookings")
    
    return jsonify(bookings)

@customer_bp.route('/booking/<booking_ref>')
def api_get_booking(booking_ref):
    """Get booking details by reference"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    results = db.execute_query("""
        SELECT b.booking_ref, b.passengers, b.total_amount, b.status, b.booking_date,
               t.from_port, t.to_port, t.departure_date, t.departure_time
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.booking_ref = %s AND b.customer_id = %s
    """, (booking_ref, session['user_id']))
    
    db.disconnect()
    
    if not results:
        return jsonify({'error': 'Booking not found'})
    
    row = results[0]
    booking = {
        'ref': row[0],
        'passengers': row[1],
        'amount': float(row[2]),
        'status': row[3],
        'date': str(row[4]),
        'from': row[5],
        'to': row[6],
        'departure_date': str(row[7]),
        'time': str(row[8]) if row[8] else 'N/A'
    }
    
    return jsonify(booking)

@customer_bp.route('/stats', methods=['GET'])
def api_get_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    stats = Booking.get_stats(session['user_id'])
    return jsonify(stats)

@customer_bp.route('/my-reservations')
def api_my_reservations():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    results = db.execute_query("""
        SELECT b.booking_ref, t.from_port, t.to_port, t.departure_date, t.departure_time, 
               b.passengers, b.total_amount, b.status
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.customer_id = %s AND t.departure_date >= CURRENT_DATE AND t.status != 'completed'
        ORDER BY t.departure_date ASC
    """, (session['user_id'],))
    
    db.disconnect()
    
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