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

@app.route('/')
def home():
    return render_template('index.html')

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
    
def init_database():
    db = Database()
    db.connect()
    
    queries = [
        # Users table
        """CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(60) NOT NULL,
            email VARCHAR(80) UNIQUE NOT NULL,
            password VARCHAR(64) NOT NULL,
            phone VARCHAR(15),
            role VARCHAR(10) DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        # Boats table
        """CREATE TABLE IF NOT EXISTS boats (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            capacity SMALLINT NOT NULL,
            status VARCHAR(12) DEFAULT 'available'
        )""",
        
        # Trips table - WALANG COMMENT SA LOOB!
        """CREATE TABLE IF NOT EXISTS trips (
            id SERIAL PRIMARY KEY,
            boat_id INTEGER REFERENCES boats(id) ON DELETE CASCADE,
            from_port VARCHAR(50) NOT NULL,
            to_port VARCHAR(50) NOT NULL,
            departure_date DATE NOT NULL,
            departure_time TIME NOT NULL,
            price NUMERIC(8,2) NOT NULL,
            available_seats SMALLINT NOT NULL,
            status VARCHAR(10) DEFAULT 'scheduled'
        )""",
        
        # Bookings table
        """CREATE TABLE IF NOT EXISTS bookings (
            id SERIAL PRIMARY KEY,
            booking_ref VARCHAR(8) UNIQUE NOT NULL,
            trip_id INTEGER REFERENCES trips(id) ON DELETE CASCADE,
            customer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            passengers SMALLINT DEFAULT 1,
            total_amount NUMERIC(8,2) NOT NULL,
            status VARCHAR(10) DEFAULT 'confirmed',
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        # Indexes for faster queries
        """CREATE INDEX IF NOT EXISTS idx_trips_search ON trips(from_port, to_port, departure_date)""",
        """CREATE INDEX IF NOT EXISTS idx_bookings_customer ON bookings(customer_id)""",
        """CREATE INDEX IF NOT EXISTS idx_trips_date ON trips(departure_date)""",
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