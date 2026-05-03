-- =============================================
-- SEA CLOUD FERRY BOOKING SYSTEM
-- PostgreSQL Database Schema
-- =============================================

-- 1. USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(20) DEFAULT 'customer', -- 'admin', 'operator', 'customer'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. BOATS TABLE
CREATE TABLE boats (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    capacity INTEGER NOT NULL,
    operator_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'available', -- 'available', 'maintenance'
    description TEXT,
    image_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TRIPS TABLE (Schedules)
CREATE TABLE trips (
    id SERIAL PRIMARY KEY,
    boat_id INTEGER REFERENCES boats(id),
    from_port VARCHAR(100) NOT NULL,
    to_port VARCHAR(100) NOT NULL,
    departure_date DATE NOT NULL,
    departure_time TIME NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    operator_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'scheduled', -- 'scheduled', 'cancelled', 'completed'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. BOOKINGS TABLE
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    trip_id INTEGER REFERENCES trips(id),
    customer_id INTEGER REFERENCES users(id),
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    passengers INTEGER DEFAULT 1,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed', -- 'confirmed', 'cancelled', 'completed'
    booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. PAYMENTS TABLE (Optional)
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    booking_id INTEGER REFERENCES bookings(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50), -- 'gcash', 'cash', 'credit_card'
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. RATINGS TABLE (For AI/Logic)
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    boat_id INTEGER REFERENCES boats(id),
    user_id INTEGER REFERENCES users(id),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- SAMPLE DATA
-- =============================================

-- Insert sample users
INSERT INTO users (name, email, password, phone, role) VALUES
('Admin User', 'admin@seacloud.com', 'admin123', '09123456789', 'admin'),
('Juan Dela Cruz', 'juan@example.com', 'juan123', '09123456780', 'customer'),
('Captain Pedro', 'pedro@boat.com', 'pedro123', '09123456781', 'operator');

-- Insert sample boats
INSERT INTO boats (name, capacity, operator_id, status, description) VALUES
('Sea Breeze 1', 50, 3, 'available', 'Airconditioned with snacks'),
('Ocean Voyager', 35, 3, 'available', 'Fast craft with life vests'),
('Island Hopper', 25, 3, 'maintenance', 'Small pumpboat for island hopping');

-- Insert sample trips
INSERT INTO trips (boat_id, from_port, to_port, departure_date, departure_time, price, operator_id) VALUES
(1, 'Butuan Port', 'Magallanes', '2025-01-20', '08:00:00', 350, 3),
(1, 'Magallanes', 'Butuan Port', '2025-01-20', '13:00:00', 350, 3),
(2, 'Butuan Port', 'Magallanes', '2025-01-21', '07:00:00', 300, 3);