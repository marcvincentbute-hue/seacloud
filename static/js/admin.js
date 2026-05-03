// ============================================
// SEACLOUD - ADMIN DASHBOARD JAVASCRIPT
// ============================================

let currentUser = {};

function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + '-page').classList.add('active');
    if (page === 'dashboard') loadDashboard();
    if (page === 'users') loadUsers();
    if (page === 'boats') loadBoats();
    if (page === 'trips') loadTrips();
    if (page === 'bookings') loadAllBookings();
}

async function loadDashboard() {
    try {
        const res = await fetch('/api/admin/stats');
        const data = await res.json();
        document.getElementById('totalUsers').textContent = data.total_users || 0;
        document.getElementById('totalBoats').textContent = data.total_boats || 0;
        document.getElementById('totalTrips').textContent = data.total_trips || 0;
        document.getElementById('totalBookings').textContent = data.total_bookings || 0;
        document.getElementById('adminName').textContent = currentUser.name || 'Admin';
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

async function loadUsers() {
    try {
        const res = await fetch('/api/admin/users');
        const users = await res.json();
        const tbody = document.getElementById('usersTableBody');
        tbody.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${u.phone || 'N/A'}</td>
                <td>${u.role}</td>
                <td><button class="btn-danger" onclick="deleteUser(${u.id})">Delete</button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

async function loadBoats() {
    try {
        const res = await fetch('/api/admin/boats');
        const boats = await res.json();
        const tbody = document.getElementById('boatsTableBody');
        tbody.innerHTML = boats.map(b => `
            <tr>
                <td>${b.id}</td>
                <td>${b.name}</td>
                <td>${b.capacity}</td>
                <td>${b.status}</td>
                <td><button class="btn-danger" onclick="deleteBoat(${b.id})">Delete</button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading boats:', error);
    }
}

async function loadTrips() {
    try {
        const res = await fetch('/api/admin/trips');
        const trips = await res.json();
        const tbody = document.getElementById('tripsTableBody');
        tbody.innerHTML = trips.map(t => `
            <tr>
                <td>${t.id}</td>
                <td>${t.from_port}</td>
                <td>${t.to_port}</td>
                <td>${t.departure_date}</td>
                <td>${t.departure_time}</td>
                <td>₱${t.price}</td>
                <td>${t.boat_name || 'N/A'}</td>
                <td><button class="btn-danger" onclick="deleteTrip(${t.id})">Delete</button></td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading trips:', error);
    }
}

async function loadAllBookings() {
    try {
        const res = await fetch('/api/admin/bookings');
        const bookings = await res.json();
        const tbody = document.getElementById('bookingsTableBody');
        tbody.innerHTML = bookings.map(b => `
            <tr>
                <td>${b.ref}</td>
                <td>${b.customer_name}</td>
                <td>${b.from_port}</td>
                <td>${b.to_port}</td>
                <td>${b.departure_date}</td>
                <td>${b.passengers}</td>
                <td>₱${b.amount}</td>
                <td>${b.status}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function showAddUserModal() { document.getElementById('userModal').style.display = 'flex'; }
function closeModal(id) { document.getElementById(id).style.display = 'none'; }

async function addUser() {
    const data = {
        name: document.getElementById('newUserName').value,
        email: document.getElementById('newUserEmail').value,
        phone: document.getElementById('newUserPhone').value,
        password: document.getElementById('newUserPassword').value,
        role: document.getElementById('newUserRole').value
    };
    try {
        const res = await fetch('/api/admin/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            alert('User added!');
            closeModal('userModal');
            loadUsers();
            loadDashboard();
            document.getElementById('addUserForm')?.reset();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('Error adding user');
    }
}

async function deleteUser(id) {
    if (confirm('Delete this user?')) {
        await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        loadUsers();
        loadDashboard();
    }
}

async function deleteBoat(id) {
    if (confirm('Delete this boat?')) {
        await fetch(`/api/admin/boats/${id}`, { method: 'DELETE' });
        loadBoats();
        loadDashboard();
    }
}

async function deleteTrip(id) {
    if (confirm('Delete this trip?')) {
        await fetch(`/api/admin/trips/${id}`, { method: 'DELETE' });
        loadTrips();
        loadDashboard();
    }
}

// ========== ADD BOAT FORM FUNCTIONS ==========
function addBoatFromForm(event) {
    event.preventDefault();
    const name = document.getElementById('newBoatNameForm').value;
    const capacity = document.getElementById('newBoatCapacityForm').value;
    const status = document.getElementById('newBoatStatusForm').value;
    
    fetch('/api/admin/boats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, capacity, status })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('Boat added successfully!');
            document.getElementById('addBoatForm').reset();
            loadBoats();
            loadDashboard();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        alert('Error adding boat');
    });
}

function clearBoatForm() {
    document.getElementById('addBoatForm').reset();
}

// ========== AUTHENTICATION ==========
async function checkAuth() {
    try {
        const res = await fetch('/api/current_user');
        const data = await res.json();
        
        if (!data.logged_in) {
            window.location.href = '/login';
            return;
        }
        
        if (data.user.role !== 'admin') {
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