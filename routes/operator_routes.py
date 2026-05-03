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
    results = db.execute_query("SELECT id, name, capacity, status FROM boats WHERE operator_id = %s", (session['user_id'],))
    db.disconnect()
    boats = [{'id': r[0], 'name': r[1], 'capacity': r[2], 'status': r[3]} for r in results]
    return jsonify(boats)

@operator_bp.route('/trips')
def api_operator_trips():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    results = db.execute_query("SELECT id, from_port, to_port, departure_date, departure_time, price FROM trips WHERE operator_id = %s", (session['user_id'],))
    db.disconnect()
    trips = [{'id': r[0], 'from_port': r[1], 'to_port': r[2], 'departure_date': str(r[3]), 'departure_time': str(r[4]), 'price': float(r[5])} for r in results]
    return jsonify(trips)

@operator_bp.route('/bookings')
def api_operator_bookings():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    db = Database()
    db.connect()
    results = db.execute_query("""
        SELECT b.booking_ref, b.customer_name, t.from_port, t.to_port, t.departure_date, b.passengers
        FROM bookings b JOIN trips t ON b.trip_id = t.id WHERE t.operator_id = %s
    """, (session['user_id'],))
    db.disconnect()
    bookings = [{'ref': r[0], 'customer_name': r[1], 'from_port': r[2], 'to_port': r[3], 'departure_date': str(r[4]), 'passengers': r[5]} for r in results]
    return jsonify(bookings)

@operator_bp.route('/income')
def api_operator_income():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    current_month = datetime.now().strftime('%Y-%m')
    results = db.execute_query("""
        SELECT COALESCE(SUM(b.total_amount), 0)
        FROM bookings b JOIN trips t ON b.trip_id = t.id
        WHERE t.operator_id = %s AND TO_CHAR(b.booking_date, 'YYYY-MM') = %s AND b.status = 'confirmed'
    """, (session['user_id'], current_month))
    current_month_income = results[0][0] if results else 0
    
    monthly_results = db.execute_query("""
        SELECT TO_CHAR(DATE_TRUNC('month', b.booking_date), 'YYYY-MM') as month,
               COUNT(DISTINCT t.id) as total_trips,
               COALESCE(SUM(b.passengers), 0) as total_passengers,
               COALESCE(SUM(b.total_amount), 0) as total_income
        FROM bookings b JOIN trips t ON b.trip_id = t.id
        WHERE t.operator_id = %s AND b.status = 'confirmed'
        GROUP BY DATE_TRUNC('month', b.booking_date)
        ORDER BY DATE_TRUNC('month', b.booking_date) DESC LIMIT 6
    """, (session['user_id'],))
    db.disconnect()
    
    income_breakdown = []
    for row in monthly_results:
        income_breakdown.append({'month': row[0], 'total_trips': row[1], 'total_passengers': row[2], 'total_income': float(row[3])})
    
    return jsonify({'current_month': datetime.now().strftime('%B %Y'), 'current_month_income': float(current_month_income), 'income_breakdown': income_breakdown})

@operator_bp.route('/boats/<int:boat_id>/status', methods=['PUT'])
def api_update_boat_status(boat_id):
    """Update boat status (available/maintenance/unavailable)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    data = request.json
    new_status = data.get('status')  # available, maintenance, unavailable
    
    valid_statuses = ['available', 'maintenance', 'unavailable']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid status'})
    
    db = Database()
    db.connect()
    
    # Check if boat belongs to operator
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    # Update boat status
    success = db.execute_insert(
        "UPDATE boats SET status = %s WHERE id = %s",
        (new_status, boat_id)
    )
    db.disconnect()
    
    if success:
        # Log the status change
        from models.audit import AuditLog
        AuditLog.log(
            user_id=session['user_id'],
            user_name=session['user_name'],
            action='UPDATE_STATUS',
            table_name='boats',
            record_id=boat_id,
            new_data=f"Status changed to {new_status}"
        )
        return jsonify({'success': True, 'message': f'Boat status updated to {new_status}'})
    
    return jsonify({'success': False, 'message': 'Failed to update status'})

@operator_bp.route('/boats/available', methods=['GET'])
def api_get_available_boats():
    """Get only available boats (for customers)"""
    db = Database()
    db.connect()
    results = db.execute_query(
        "SELECT id, name, capacity FROM boats WHERE status = 'available' AND is_deleted = FALSE"
    )
    db.disconnect()
    
    boats = [{'id': r[0], 'name': r[1], 'capacity': r[2]} for r in results]
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
    
    # Check boat ownership
    result = db.execute_query(
        "SELECT id FROM boats WHERE id = %s AND operator_id = %s",
        (boat_id, session['user_id'])
    )
    
    if not result:
        db.disconnect()
        return jsonify({'success': False, 'message': 'Boat not found'})
    
    # Update status to maintenance
    success = db.execute_insert(
        "UPDATE boats SET status = 'maintenance' WHERE id = %s",
        (boat_id,)
    )
    
    # Log maintenance report
    if success:
        from models.audit import AuditLog
        AuditLog.log(
            user_id=session['user_id'],
            user_name=session['user_name'],
            action='MAINTENANCE',
            table_name='boats',
            record_id=boat_id,
            new_data=f"Maintenance: {reason}, Estimated days: {estimated_days}"
        )
    
    db.disconnect()
    
    if success:
        return jsonify({'success': True, 'message': 'Boat marked for maintenance'})
    return jsonify({'success': False, 'message': 'Failed to update'})