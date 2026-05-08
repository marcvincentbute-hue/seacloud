from flask import Blueprint, request, jsonify, session
from models.database import Database
from models.user import User
from models.boat import Boat
from models.trip import Trip
from models.auth import Auth

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats')
def api_admin_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    total_users = db.execute_query("SELECT COUNT(*) FROM users")[0][0]
    total_boats = db.execute_query("SELECT COUNT(*) FROM boats")[0][0]
    total_trips = db.execute_query("SELECT COUNT(*) FROM trips")[0][0]
    total_bookings = db.execute_query("SELECT COUNT(*) FROM bookings")[0][0]
    db.disconnect()
    
    return jsonify({'total_users': total_users, 'total_boats': total_boats, 'total_trips': total_trips, 'total_bookings': total_bookings})

@admin_bp.route('/users')
def api_admin_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    users = User.get_all()
    return jsonify([u.to_dict() for u in users])

@admin_bp.route('/users', methods=['POST'])
def api_admin_add_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    data = request.json
    result = Auth.register(
        name=data.get('name'), email=data.get('email'), password=data.get('password'),
        phone=data.get('phone', ''), role=data.get('role', 'customer')
    )
    return jsonify(result)

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def api_admin_delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    user = User.find_by_id(user_id)
    if user:
        user.delete()
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/boats')
def api_admin_boats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    results = db.execute_query("SELECT id, name, capacity, status FROM boats")
    db.disconnect()
    boats = [{'id': r[0], 'name': r[1], 'capacity': r[2], 'status': r[3]} for r in results]
    return jsonify(boats)

@admin_bp.route('/boats', methods=['POST'])
def api_admin_add_boat():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    data = request.json
    boat = Boat(name=data.get('name'), capacity=data.get('capacity'), status=data.get('status', 'available'))
    if boat.save():
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/boats/<int:boat_id>', methods=['DELETE'])
def api_admin_delete_boat(boat_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    boat = Boat.find_by_id(boat_id)
    if boat:
        boat.delete()
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/trips')
def api_admin_trips():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    results = db.execute_query("""
        SELECT t.id, t.from_port, t.to_port, t.departure_date, t.departure_time, t.price, b.name
        FROM trips t JOIN boats b ON t.boat_id = b.id
    """)
    db.disconnect()
    trips = [{'id': r[0], 'from_port': r[1], 'to_port': r[2], 'departure_date': str(r[3]), 'departure_time': str(r[4]), 'price': float(r[5]), 'boat_name': r[6]} for r in results]
    return jsonify(trips)

@admin_bp.route('/trips', methods=['POST'])
def api_admin_add_trip():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    data = request.json
    trip = Trip(boat_id=data.get('boat_id'), from_port=data.get('from_port'), to_port=data.get('to_port'), departure_date=data.get('departure_date'), departure_time=data.get('departure_time'), price=data.get('price'))
    if trip.save():
        return jsonify({'success': True})
    return jsonify({'success': False})

@admin_bp.route('/bookings')
def api_admin_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    # FIXED: Walang customer_name sa bookings table, gamitin ang users table
    results = db.execute_query("""
        SELECT b.booking_ref, u.name, t.from_port, t.to_port, t.departure_date, b.passengers, b.total_amount, b.status
        FROM bookings b 
        JOIN trips t ON b.trip_id = t.id 
        JOIN users u ON b.customer_id = u.id
        ORDER BY b.booking_date DESC
    """)
    db.disconnect()
    bookings = [{'ref': r[0], 'customer_name': r[1], 'from_port': r[2], 'to_port': r[3], 'departure_date': str(r[4]), 'passengers': r[5], 'amount': float(r[6]), 'status': r[7]} for r in results]
    return jsonify(bookings)

@admin_bp.route('/trips/<int:trip_id>', methods=['DELETE'])
def api_admin_delete_trip(trip_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    # Simplified: No AuditLog
    db = Database()
    db.connect()
    db.execute_insert("DELETE FROM trips WHERE id = %s", (trip_id,))
    db.disconnect()
    return jsonify({'success': True})

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def api_admin_update_user(user_id):
    """Update a user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role')
    
    db = Database()
    db.connect()
    
    # Check if user exists
    result = db.execute_query("SELECT id FROM users WHERE id = %s", (user_id,))
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'User not found'})
    
    # Update user
    success = db.execute_insert("""
        UPDATE users SET name = %s, email = %s, phone = %s, role = %s WHERE id = %s
    """, (name, email, phone, role, user_id))
    
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'User updated successfully'})
    return jsonify({'success': False, 'message': 'Failed to update user'})

@admin_bp.route('/trips/<int:trip_id>', methods=['PUT'])
def api_admin_update_trip(trip_id):
    """Update a trip"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    boat_id = data.get('boat_id')
    from_port = data.get('from_port')
    to_port = data.get('to_port')
    departure_date = data.get('departure_date')
    departure_time = data.get('departure_time')
    price = data.get('price')
    available_seats = data.get('available_seats')
    
    db = Database()
    db.connect()
    
    # Check if trip exists
    result = db.execute_query("SELECT id FROM trips WHERE id = %s", (trip_id,))
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Trip not found'})
    
    # Update trip
    success = db.execute_insert("""
        UPDATE trips 
        SET boat_id = %s, from_port = %s, to_port = %s, 
            departure_date = %s, departure_time = %s, 
            price = %s, available_seats = %s
        WHERE id = %s
    """, (boat_id, from_port, to_port, departure_date, departure_time, price, available_seats, trip_id))
    
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'Trip updated successfully'})
    return jsonify({'success': False, 'message': 'Failed to update trip'})

@admin_bp.route('/boats/<int:boat_id>', methods=['PUT'])
def api_admin_update_boat(boat_id):
    """Update a boat"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    name = data.get('name')
    capacity = data.get('capacity')
    status = data.get('status')
    
    db = Database()
    db.connect()
    
    # Check if boat exists
    result = db.execute_query("SELECT id FROM boats WHERE id = %s", (boat_id,))
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    # Update boat
    success = db.execute_insert("""
        UPDATE boats SET name = %s, capacity = %s, status = %s WHERE id = %s
    """, (name, capacity, status, boat_id))
    
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'Boat updated successfully'})
    return jsonify({'success': False, 'message': 'Failed to update boat'})