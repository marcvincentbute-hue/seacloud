from flask import Blueprint, render_template, session, make_response

page_bp = Blueprint('page', __name__)

@page_bp.route('/')
def home():
    return render_template('index.html')

@page_bp.route('/login')
def login_page():
    return render_template('login.html')

@page_bp.route('/register')
def register_page():
    return render_template('register.html')

@page_bp.route('/customer/dashboard')
def customer_dashboard():
    print(f"🔍 Session check - user_id: {session.get('user_id')}")
    if 'user_id' not in session:
        print("❌ No user_id in session, redirecting to login")
        return render_template('login.html')
    print("✅ User is logged in, showing dashboard")
    response = make_response(render_template('customer_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@page_bp.route('/admin/dashboard')
def admin_dashboard_page():
    print(f"🔍 Session check - user_id: {session.get('user_id')}")
    if 'user_id' not in session:
        print("❌ No user_id in session, redirecting to login")
        return render_template('login.html')
    print("✅ User is logged in, showing admin dashboard")
    response = make_response(render_template('admin_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@page_bp.route('/operator/dashboard')
def operator_dashboard_page():
    print(f"🔍 Session check - user_id: {session.get('user_id')}")
    if 'user_id' not in session:
        print("❌ No user_id in session, redirecting to login")
        return render_template('login.html')
    print("✅ User is logged in, showing operator dashboard")
    response = make_response(render_template('operator_dashboard.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response
