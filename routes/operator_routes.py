from flask import Blueprint, request, jsonify, session
from models.database import Database
from datetime import datetime

operator_bp = Blueprint('operator', __name__, url_prefix='/api/operator')

@operator_bp.route('/stats')
def api_operator_stats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    total_boats = db.execute_query("SELECT COUNT(*) FROM boats WHERE operator_id = %s", (session['user_id'],))
    total_boats = total_boats[0][0] if total_boats else 0
    total_trips = db.execute_query("SELECT COUNT(*) FROM trips WHERE operator_id = %s", (session['user_id'],))
    total_trips = total_trips[0][0] if total_trips else 0
    total_bookings = db.execute_query("SELECT COUNT(*) FROM bookings b JOIN trips t ON b.trip_id = t.id WHERE t.operator_id = %s", (session['user_id'],))
    total_bookings = total_bookings[0][0] if total_bookings else 0
    db.disconnect()
    
    return jsonify({'total_boats': total_boats, 'total_trips': total_trips, 'total_bookings': total_bookings})

@operator_bp.route('/boats')
def api_operator_boats():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    
    results = db.execute_query("""
        SELECT id, name, capacity, status 
        FROM boats 
        WHERE operator_id = %s
    """, (session['user_id'],))
    
    db.disconnect()
    
    boats = []
    if results:
        boats = [{'id': r[0], 'name': r[1], 'capacity': r[2], 'status': r[3]} for r in results]
    
    return jsonify(boats)

@operator_bp.route('/boats', methods=['POST'])
def api_operator_add_boat():
    """Add a new boat for the operator"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    name = data.get('name')
    capacity = data.get('capacity')
    status = data.get('status', 'available')
    
    if not name or not capacity:
        return jsonify({'success': False, 'message': 'Name and capacity required'})
    
    db = Database()
    db.connect()
    
    try:
        db.execute_insert("""
            INSERT INTO boats (name, capacity, operator_id, status)
            VALUES (%s, %s, %s, %s)
        """, (name, capacity, session['user_id'], status))
        db.disconnect()
        return jsonify({'success': True, 'message': 'Boat added successfully'})
    except Exception as e:
        db.disconnect()
        print(f"Error adding boat: {e}")
        return jsonify({'success': False, 'message': str(e)})

@operator_bp.route('/boats/<int:boat_id>', methods=['DELETE'])
def api_operator_delete_boat(boat_id):
    """Delete a boat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    success = db.execute_insert("DELETE FROM boats WHERE id = %s", (boat_id,))
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'Boat deleted successfully'})
    return jsonify({'success': False, 'message': 'Failed to delete boat'})

@operator_bp.route('/boats/<int:boat_id>', methods=['PUT'])
def api_operator_update_boat(boat_id):
    """Update a boat"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    name = data.get('name')
    capacity = data.get('capacity')
    status = data.get('status')
    
    db = Database()
    db.connect()
    
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    success = db.execute_insert(
        "UPDATE boats SET name = %s, capacity = %s, status = %s WHERE id = %s",
        (name, capacity, status, boat_id)
    )
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'Boat updated successfully'})
    return jsonify({'success': False, 'message': 'Failed to update boat'})

@operator_bp.route('/trips')
def api_operator_trips():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    results = db.execute_query("""
        SELECT t.id, t.from_port, t.to_port, t.departure_date, t.departure_time, t.price, t.available_seats, b.name as boat_name, t.status
        FROM trips t
        JOIN boats b ON t.boat_id = b.id
        WHERE t.operator_id = %s AND t.status != 'completed'
        ORDER BY t.departure_date DESC
    """, (session['user_id'],))
    db.disconnect()
    
    trips = []
    if results:
        for row in results:
            trips.append({
                'id': row[0],
                'from_port': row[1],
                'to_port': row[2],
                'departure_date': str(row[3]),
                'departure_time': str(row[4])[:5] if row[4] else 'N/A',
                'price': float(row[5]),
                'available_seats': row[6],
                'boat_name': row[7],
                'status': row[8]
            })
    
    return jsonify(trips)

@operator_bp.route('/trips', methods=['POST'])
def api_operator_add_trip():
    """Add a new trip for the operator"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    boat_id = data.get('boat_id')
    from_port = data.get('from_port')
    to_port = data.get('to_port')
    departure_date = data.get('departure_date')
    departure_time = data.get('departure_time')
    price = data.get('price')
    available_seats = data.get('available_seats')
    
    print(f"📝 Adding trip: {from_port} → {to_port}, boat_id: {boat_id}")
    
    if not all([boat_id, from_port, to_port, departure_date, departure_time, price, available_seats]):
        return jsonify({'success': False, 'message': 'All fields required'})
    
    db = Database()
    db.connect()
    
    try:
        db.execute_insert("""
            INSERT INTO trips (boat_id, from_port, to_port, departure_date, departure_time, price, available_seats, status, operator_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'scheduled', %s)
        """, (boat_id, from_port, to_port, departure_date, departure_time, price, available_seats, session['user_id']))
        
        db.disconnect()
        print("✅ Trip added successfully!")
        return jsonify({'success': True, 'message': 'Trip added successfully'})
    except Exception as e:
        db.disconnect()
        print(f"❌ Error adding trip: {e}")
        return jsonify({'success': False, 'message': str(e)})

@operator_bp.route('/bookings')
def api_operator_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    # FIXED: Gamitin ang boat.operator_id para makuha ang operator's bookings
    results = db.execute_query("""
        SELECT b.booking_ref, u.name, t.from_port, t.to_port, t.departure_date, b.passengers
        FROM bookings b 
        JOIN trips t ON b.trip_id = t.id 
        JOIN boats bo ON t.boat_id = bo.id
        JOIN users u ON b.customer_id = u.id
        WHERE bo.operator_id = %s
        ORDER BY t.departure_date DESC
    """, (session['user_id'],))
    
    db.disconnect()
    
    bookings = []
    if results:
        for row in results:
            bookings.append({
                'ref': row[0],
                'customer_name': row[1],
                'from_port': row[2],
                'to_port': row[3],
                'departure_date': str(row[4]),
                'passengers': row[5]
            })
    
    return jsonify(bookings)

@operator_bp.route('/boats/<int:boat_id>/status', methods=['PUT'])
def api_update_boat_status(boat_id):
    """Update boat status (available/maintenance/unavailable)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    new_status = data.get('status')
    
    valid_statuses = ['available', 'maintenance', 'unavailable']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    db = Database()
    db.connect()
    
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    success = db.execute_insert(
        "UPDATE boats SET status = %s WHERE id = %s",
        (new_status, boat_id)
    )
    db.disconnect()
    
    if success:
        print(f"Boat {boat_id} status updated to {new_status} by operator {session['user_id']}")
        return jsonify({'success': True, 'message': f'Boat status updated to {new_status}'})
    
    return jsonify({'success': False, 'message': 'Failed to update status'})

@operator_bp.route('/boats/available', methods=['GET'])
def api_get_available_boats():
    """Get only available boats (for customers)"""
    db = Database()
    db.connect()
    results = db.execute_query(
        "SELECT id, name, capacity FROM boats WHERE status = 'available'"
    )
    db.disconnect()
    
    boats = [{'id': r[0], 'name': r[1], 'capacity': r[2]} for r in results] if results else []
    return jsonify(boats)

@operator_bp.route('/boats/maintenance', methods=['POST'])
def api_report_maintenance():
    """Report a boat under maintenance"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    boat_id = data.get('boat_id')
    reason = data.get('reason', '')
    estimated_days = data.get('estimated_days', 0)
    
    db = Database()
    db.connect()
    
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    success = db.execute_insert(
        "UPDATE boats SET status = 'maintenance' WHERE id = %s",
        (boat_id,)
    )
    db.disconnect()
    
    if success:
        print(f"Boat {boat_id} marked for maintenance by operator {session['user_id']}: {reason}")
        return jsonify({'success': True, 'message': 'Boat marked for maintenance'})
    return jsonify({'success': False, 'message': 'Failed to update'})

@operator_bp.route('/trips/<int:trip_id>/complete', methods=['PUT'])
def api_complete_trip(trip_id):
    """Mark a trip as completed"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    print(f"📝 Completing trip {trip_id} for operator {session['user_id']}")
    
    db = Database()
    db.connect()
    
    # Check if trip belongs to operator
    result = db.execute_query(
        "SELECT id FROM trips WHERE id = %s AND operator_id = %s",
        (trip_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Trip not found'})
    
    # Update status to completed
    success = db.execute_insert(
        "UPDATE trips SET status = 'completed' WHERE id = %s",
        (trip_id,)
    )
    db.disconnect()
    
    if success:
        print(f"✅ Trip {trip_id} marked as completed")
        return jsonify({'success': True, 'message': 'Trip marked as completed'})
    
    return jsonify({'success': False, 'message': 'Failed to complete trip'})