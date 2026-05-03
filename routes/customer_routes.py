from flask import Blueprint, request, jsonify, session
from models.trip import Trip
from models.booking import Booking
from models.user import User

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