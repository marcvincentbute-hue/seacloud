from flask import Blueprint, request, jsonify, session, render_template
from config import Config
import psycopg2
from psycopg2 import OperationalError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import time

forgot_bp = Blueprint('forgot', __name__)

# Gmail configuration
GMAIL_USER = "Sea.cloud2026@gmail.com" 
GMAIL_PASSWORD = "hmgi pbch eusu yxeg" 

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

def send_reset_email(to_email, reset_link):
    """Send password reset email via Gmail"""
    try:
        # Create email
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = "SeaCloud - Password Reset Request"
        
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 500px; margin: 0 auto; padding: 20px; background: #f0f2f5; border-radius: 10px;">
                <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #0077b6, #00b8d4); border-radius: 10px;">
                    <h2 style="color: white;">⛴️ SeaCloud</h2>
                </div>
                <div style="background: white; padding: 20px; border-radius: 10px; margin-top: 10px;">
                    <h3>Password Reset Request</h3>
                    <p>You requested to reset your password. Click the button below to reset it:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background: linear-gradient(135deg, #0077b6, #00b8d4); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px;">Reset Password</a>
                    </div>
                    <p>Or copy this link: <a href="{reset_link}">{reset_link}</a></p>
                    <p>This link will expire in 1 hour.</p>
                    <p>If you did not request this, please ignore this email.</p>
                    <hr>
                    <p style="font-size: 12px; color: #666;">SeaCloud Ferry Booking System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

@forgot_bp.route('/forgot-password')
def forgot_password_page():
    return render_template('forgot_password.html')

@forgot_bp.route('/reset-password')
def reset_password_page():
    token = request.args.get('token')
    if not token:
        return render_template('login.html')
    
    # Verify token (simplified)
    if session.get('reset_token') == token:
        return render_template('reset_password.html', token=token)
    return render_template('login.html')

@forgot_bp.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    email = data.get('email')
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    
    if user:
        # Generate reset token
        token = hashlib.md5(f"{email}{time.time()}".encode()).hexdigest()
        session['reset_email'] = email
        session['reset_token'] = token
        
        # Generate reset link
        reset_link = f"https://your-ngrok-url.ngrok-free.app/reset-password?token={token}"
        
        # Send email
        if send_reset_email(email, reset_link):
            cur.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Password reset link sent to your email!'})
        else:
            cur.close()
            conn.close()
            return jsonify({'success': False, 'message': 'Failed to send email. Please try again.'})
    else:
        cur.close()
        conn.close()
        return jsonify({'success': False, 'message': 'Email address not found!'})


@forgot_bp.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('new_password')
    
    if session.get('reset_token') != token:
        return jsonify({'success': False, 'message': 'Invalid or expired token'})
    
    email = session.get('reset_email')
    if not email:
        return jsonify({'success': False, 'message': 'Session expired'})
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = %s WHERE email = %s", (new_password, email))
    conn.commit()
    
    session.pop('reset_email', None)
    session.pop('reset_token', None)
    
    cur.close()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password reset successfully! You can now login.'})