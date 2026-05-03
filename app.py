from flask import Flask, render_template
from flask_cors import CORS
from config import Config
import os
import psycopg2
from psycopg2 import OperationalError

from models.database import Database
from routes import register_routes

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
app.secret_key = Config.SECRET_KEY
CORS(app)

# ========== DIRECT HOME ROUTE (ADD THIS) ==========
@app.route('/')
def home():
    return render_template('index.html')

# ========== DATABASE CONNECTION FUNCTION ==========
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
    
# ========== INITIALIZE DATABASE TABLES ==========
def init_database():
    db = Database()
    db.connect()
    queries = [
        "CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(30) NOT NULL, email VARCHAR(20) UNIQUE NOT NULL, password VARCHAR(18) NOT NULL, phone VARCHAR(11), role VARCHAR(20) DEFAULT 'customer', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS boats (id SERIAL PRIMARY KEY, name VARCHAR(30) NOT NULL, capacity INT NOT NULL, operator_id INT REFERENCES users(id), status VARCHAR(20) DEFAULT 'available', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS trips (id SERIAL PRIMARY KEY, boat_id INT REFERENCES boats(id), from_port VARCHAR(15) NOT NULL, to_port VARCHAR(15) NOT NULL, departure_date DATE NOT NULL, departure_time TIME NOT NULL, price DECIMAL(10,2) NOT NULL, operator_id INT REFERENCES users(id), status VARCHAR(20) DEFAULT 'scheduled', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
        "CREATE TABLE IF NOT EXISTS bookings (id SERIAL PRIMARY KEY, booking_ref VARCHAR(30) UNIQUE NOT NULL, trip_id INT REFERENCES trips(id), customer_id INT REFERENCES users(id), customer_name VARCHAR(30) NOT NULL, customer_email VARCHAR(20) NOT NULL, passengers INT DEFAULT 1, total_amount DECIMAL(10,2) NOT NULL, status VARCHAR(20) DEFAULT 'confirmed', booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    ]
    for query in queries:
        db.execute_insert(query)
    db.disconnect()
    print("✅ Database initialized!")

init_database()

# Register all routes
register_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)