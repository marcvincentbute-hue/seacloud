from flask import Blueprint, request, jsonify, session
from models.database import Database
from datetime import datetime

notification_bp = Blueprint('notification', __name__, url_prefix='/api')

@notification_bp.route('/notifications', methods=['GET'])
def get_notifications():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    
    results = db.execute_query("""
        SELECT id, title, message, icon, color, bg, is_read, 
               TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') as created_at
        FROM notifications
        WHERE user_id = %s OR user_id IS NULL
        ORDER BY created_at DESC
        LIMIT 20
    """, (session['user_id'],))
    
    db.disconnect()
    
    notifications = []
    for row in results:
        # Format time ago
        created = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        diff = now - created
        if diff.days > 0:
            time_ago = f"{diff.days} day(s) ago"
        elif diff.seconds > 3600:
            time_ago = f"{diff.seconds // 3600} hour(s) ago"
        elif diff.seconds > 60:
            time_ago = f"{diff.seconds // 60} minute(s) ago"
        else:
            time_ago = "Just now"
        
        notifications.append({
            'id': row[0],
            'title': row[1],
            'message': row[2],
            'icon': row[3],
            'color': row[4],
            'bg': row[5],
            'read': row[6],
            'time': time_ago
        })
    
    return jsonify(notifications)

@notification_bp.route('/notifications/<int:notif_id>/read', methods=['POST'])
def mark_as_read(notif_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    db.execute_insert("UPDATE notifications SET is_read = TRUE WHERE id = %s", (notif_id,))
    db.disconnect()
    
    return jsonify({'success': True})

@notification_bp.route('/notifications/read-all', methods=['POST'])
def mark_all_read():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'})
    
    db = Database()
    db.connect()
    db.execute_insert("UPDATE notifications SET is_read = TRUE WHERE user_id = %s OR user_id IS NULL", (session['user_id'],))
    db.disconnect()
    
    return jsonify({'success': True})

def create_notification(user_id, title, message, icon='bell', color='#059669', bg='#ecfdf5'):
    """Helper function to create notification"""
    db = Database()
    db.connect()
    db.execute_insert("""
        INSERT INTO notifications (user_id, title, message, icon, color, bg)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, title, message, icon, color, bg))
    db.disconnect()