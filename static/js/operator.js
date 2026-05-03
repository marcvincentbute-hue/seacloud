// ============================================
// SEACLOUD - OPERATOR DASHBOARD JAVASCRIPT
// ============================================

let currentUser = {};

// ========== MONTHLY INCOME FUNCTIONS (UNA UNA) ==========
async function loadMonthlyIncome() {
    try {
        const response = await fetch('/api/operator/income');
        const data = await response.json();
        
        const monthlyIncomeElem = document.getElementById('monthlyIncome');
        const incomeMonthElem = document.getElementById('incomeMonth');
        const incomeBreakdownElem = document.getElementById('incomeBreakdown');
        
        if (monthlyIncomeElem) {
            monthlyIncomeElem.innerHTML = `₱${data.current_month_income.toLocaleString()}`;
        }
        if (incomeMonthElem) {
            incomeMonthElem.innerHTML = data.current_month;
        }
        if (incomeBreakdownElem) {
            incomeBreakdownElem.innerHTML = data.income_breakdown.map(item => `
                <tr>
                    <td>${item.month}</td>
                    <td>${item.total_trips}</td>
                    <td>${item.total_passengers}</td>
                    <td><strong>₱${item.total_income.toLocaleString()}</strong></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading income:', error);
    }
}

// ========== DASHBOARD FUNCTIONS ==========
async function loadDashboard() {
    try {
        const response = await fetch('/api/operator/stats');
        const data = await response.json();
        document.getElementById('totalBoats').textContent = data.total_boats || 0;
        document.getElementById('totalTrips').textContent = data.total_trips || 0;
        document.getElementById('totalBookings').textContent = data.total_bookings || 0;
        document.getElementById('welcomeMsg').innerHTML = `Welcome back, ${currentUser.name}! 👋`;
        
        // Load monthly income
        await loadMonthlyIncome();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadBoats() {
    try {
        const response = await fetch('/api/operator/boats');
        const boats = await response.json();
        const tbody = document.getElementById('boatsTable');
        
        if (boats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">No boats found</td></tr>';
        } else {
            tbody.innerHTML = boats.map(b => `
                <tr>
                    <td>${b.id}</td>
                    <td><strong>${b.name}</strong></td>
                    <td>${b.capacity} seats</td>
                    <td><span class="badge ${b.status === 'available' ? 'badge-success' : 'badge-danger'}">${b.status}</span></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading boats:', error);
    }
}

async function loadTrips() {
    try {
        const response = await fetch('/api/operator/trips');
        const trips = await response.json();
        const tbody = document.getElementById('tripsTable');
        
        if (trips.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No trips found</td></tr>';
        } else {
            tbody.innerHTML = trips.map(t => `
                <tr>
                    <td>${t.id}</td>
                    <td>${t.from_port}</td>
                    <td>${t.to_port}</td>
                    <td>${t.departure_date}</td>
                    <td>${t.departure_time}</td>
                    <td><strong>₱${t.price}</strong></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading trips:', error);
    }
}

async function loadBookings() {
    try {
        const response = await fetch('/api/operator/bookings');
        const bookings = await response.json();
        const tbody = document.getElementById('bookingsTable');
        
        if (bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center">No bookings found</td></tr>';
        } else {
            tbody.innerHTML = bookings.map(b => `
                <tr>
                    <td><strong>${b.ref}</strong></td>
                    <td>${b.customer_name}</td>
                    <td>${b.from_port}</td>
                    <td>${b.to_port}</td>
                    <td>${b.departure_date}</td>
                    <td>${b.passengers} passenger(s)</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + '-page').classList.add('active');
    if (page === 'dashboard') loadDashboard();
    if (page === 'boats') loadBoats();
    if (page === 'trips') loadTrips();
    if (page === 'bookings') loadBookings();
}

// ========== AUTHENTICATION ==========
async function checkAuth() {
    try {
        const response = await fetch('/api/current_user');
        const data = await response.json();
        
        if (!data.logged_in) {
            window.location.href = '/login';
            return;
        }
        
        if (data.user.role !== 'operator') {
            window.location.href = '/login';
            return;
        }
        
        currentUser = data.user;
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
        loadDashboard();
        
    } catch (error) {
        console.error('Auth error:', error);
        window.location.href = '/login';
    }
}

// Prevent back button after logout
(function() {
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function() {
        window.history.pushState(null, "", window.location.href);
        if (!sessionStorage.getItem('currentUser')) {
            window.location.href = '/login';
        }
    };
})();

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    if (!sessionStorage.getItem('currentUser')) {
        window.location.href = '/login';
    }
});

// Initialize
checkAuth();