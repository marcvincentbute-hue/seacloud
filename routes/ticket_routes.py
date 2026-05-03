from flask import Blueprint, send_file, session, jsonify
from models.database import Database
from models.booking import Booking
import qrcode
from io import BytesIO
import base64

ticket_bp = Blueprint('ticket', __name__, url_prefix='/ticket')

@ticket_bp.route('/view/<booking_ref>')
def view_ticket(booking_ref):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    booking = db.execute_query("""
        SELECT b.booking_ref, b.customer_name, b.passengers, b.total_amount, 
               t.from_port, t.to_port, t.departure_date, t.departure_time, b.booking_date
        FROM bookings b
        JOIN trips t ON b.trip_id = t.id
        WHERE b.booking_ref = %s AND b.customer_id = %s
    """, (booking_ref, session['user_id']))
    
    db.disconnect()
    
    if not booking:
        return jsonify({'error': 'Booking not found'})
    
    # Generate QR Code
    qr_data = f"SEACLOUD|{booking_ref}|{booking[0][5]}|{booking[0][6]}|{booking[0][4]}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0077b6", back_color="white")
    
    # Convert QR to base64
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    ticket_data = {
        'ref': booking[0][0],
        'name': booking[0][1],
        'passengers': booking[0][2],
        'amount': float(booking[0][3]),
        'from': booking[0][4],
        'to': booking[0][5],
        'date': str(booking[0][6]),
        'time': str(booking[0][7]),
        'booked_date': str(booking[0][8]),
        'qr_code': qr_base64
    }
    
    return jsonify(ticket_data)