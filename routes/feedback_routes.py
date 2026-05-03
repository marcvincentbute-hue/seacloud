from flask import Blueprint, request, jsonify
from models.database import Database

feedback_bp = Blueprint('feedback', __name__, url_prefix='/api')

@feedback_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.json
        rating = data.get('rating')
        name = data.get('name', '')
        email = data.get('email', '')
        message = data.get('message')
        
        db = Database()
        db.connect()
        query = """
            INSERT INTO feedback (rating, name, email, message)
            VALUES (%s, %s, %s, %s)
        """
        success = db.execute_insert(query, (rating, name, email, message))
        db.disconnect()
        
        if success:
            return jsonify({'success': True, 'message': 'Feedback submitted!'})
        return jsonify({'success': False, 'message': 'Failed to submit feedback'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})