from flask import Blueprint, request, jsonify, session
from models.user import User
from models.auth import Auth
from config import Config
import psycopg2
from psycopg2 import OperationalError

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

# Database connection function
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            port=Config.DB_PORT
        )
        return conn
    except OperationalError as e:
        print(f"Database error: {e}")
        return None

@auth_bp.route('/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        result = Auth.register(
            name=data.get('name'),
            email=data.get('email'),
            password=data.get('password'),
            phone=data.get('phone', ''),
            role=data.get('role', 'customer')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        print(f"🔐 Login attempt: {email}")
        
        conn = get_db_connection()
        if conn is None:
            print("❌ Database connection failed")
            return jsonify({'success': False, 'message': 'Database connection failed'})
        
        cur = conn.cursor()
        cur.execute("SELECT id, name, email, role FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        
        print(f"📝 User found: {user}")
        
        cur.close()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_role'] = user[3]
            return jsonify({
                'success': True, 
                'message': 'Login successful!', 
                'role': user[3],
                'user_id': user[0],
                'user_name': user[1]
            })
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'message': str(e)})
    
@auth_bp.route('/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

@auth_bp.route('/current_user')
def api_current_user():
    if 'user_id' in session:
        user = User.find_by_id(session['user_id'])
        return jsonify({'logged_in': True, 'user': user.to_dict() if user else None})
    return jsonify({'logged_in': False})

@auth_bp.route('/update_profile', methods=['POST'])
def api_update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.json
    user = User.find_by_id(session['user_id'])
    
    if user:
        user.name = data.get('name', user.name)
        user.phone = data.get('phone', user.phone)
        if user.update():
            session['user_name'] = user.name
            return jsonify({'success': True, 'message': 'Profile updated!'})
    
    return jsonify({'success': False, 'message': 'Update failed!'})