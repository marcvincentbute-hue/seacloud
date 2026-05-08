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
                <td style="padding: 12px;">${u.id}</td>
                <td style="padding: 12px;">${u.name}</td>
                <td style="padding: 12px;">${u.email}</td>
                <td style="padding: 12px;">${u.phone || 'N/A'}</td>
                <td style="padding: 12px;">${u.role}</td>
                <td style="padding: 12px; white-space: nowrap;">
                    <button onclick="openEditUserModal(${u.id}, '${u.name}', '${u.email}', '${u.phone}', '${u.role}')" style="background: #ffc107; color: #333; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer; margin-right: 5px;">Edit</button>
                    <button onclick="deleteUser(${u.id})" style="background: #dc3545; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;">Delete</button>
                </td>
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
        
        if (boats.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">No boats found</td></tr>';
        } else {
            tbody.innerHTML = boats.map(b => `
                <tr>
                    <td style="padding: 12px;"><strong>${b.name}</strong></td>
                    <td style="padding: 12px;">${b.capacity} seats</td>
                    <td style="padding: 12px;"><span class="badge ${b.status === 'available' ? 'badge-success' : 'badge-warning'}">${b.status}</span></td>
                    <td style="padding: 12px; white-space: nowrap;">
                        <button onclick="openEditBoatModalAdmin(${b.id}, '${b.name}', ${b.capacity}, '${b.status}')" style="background: #ffc107; color: #333; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer; margin-right: 5px;">Edit</button>
                        <button onclick="deleteBoat(${b.id})" style="background: #dc3545; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;">Delete</button>
                    </td>
                 `
            ).join('');
        }
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
                <td style="padding: 12px;">${t.id}</td>
                <td style="padding: 12px;">${t.boat_name || 'N/A'}</td>
                <td style="padding: 12px;">${t.from_port}</td>
                <td style="padding: 12px;">${t.to_port}</td>
                <td style="padding: 12px;">${t.departure_date}</td>
                <td style="padding: 12px;">${t.departure_time}</td>
                <td style="padding: 12px;">₱${t.price}</td>
                <td style="padding: 12px;">${t.available_seats}</td>
                <td style="padding: 12px;">${t.status || 'scheduled'}</td>
                <td style="padding: 12px; white-space: nowrap;">
                    <button onclick='openEditTripModal(${JSON.stringify(t)})' style="background: #ffc107; color: #333; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer; margin-right: 5px;">Edit</button>
                    <button onclick="deleteTrip(${t.id})" style="background: #dc3545; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;">Delete</button>
                </td>
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

// Edit Boat Function
async function editBoat(boatId) {
    const newName = prompt('Enter new boat name:');
    if (!newName) return;
    
    const newCapacity = prompt('Enter new capacity:');
    if (!newCapacity) return;
    
    const newStatus = prompt('Enter new status (available/maintenance/inactive):');
    if (!newStatus) return;
    
    try {
        const response = await fetch(`/api/admin/boats/${boatId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, capacity: parseInt(newCapacity), status: newStatus })
        });
        
        const result = await response.json();
        if (result.success) {
            alert('Boat updated successfully!');
            loadBoats();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        alert('Error updating boat');
    }
}

// ========== EDIT USER FUNCTIONS ==========
function openEditUserModal(userId, name, email, phone, role) {
    document.getElementById('editUserId').value = userId;
    document.getElementById('editUserName').value = name;
    document.getElementById('editUserEmail').value = email;
    document.getElementById('editUserPhone').value = phone || '';
    document.getElementById('editUserRole').value = role;
    document.getElementById('editUserModal').style.display = 'flex';
}

function closeEditUserModal() {
    document.getElementById('editUserModal').style.display = 'none';
}

async function updateUser(event) {
    event.preventDefault();
    
    const id = document.getElementById('editUserId').value;
    const name = document.getElementById('editUserName').value;
    const email = document.getElementById('editUserEmail').value;
    const phone = document.getElementById('editUserPhone').value;
    const role = document.getElementById('editUserRole').value;
    
    try {
        const response = await fetch(`/api/admin/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, role })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('User updated successfully!');
            closeEditUserModal();
            loadUsers();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating user:', error);
        alert('Failed to update user');
    }
}
// Close modal when clicking outside
window.onclick = function(event) {
    const userModal = document.getElementById('userModal');
    const editUserModal = document.getElementById('editUserModal');
    const addBoatModal = document.getElementById('addBoatModalAdmin');
    const editBoatModal = document.getElementById('editBoatModalAdmin');
    const addTripModal = document.getElementById('addTripModalAdmin');
    const editTripModal = document.getElementById('editTripModalAdmin');
    
    if (event.target === userModal) userModal.style.display = 'none';
    if (event.target === editUserModal) editUserModal.style.display = 'none';
    if (event.target === addBoatModal) addBoatModal.style.display = 'none';
    if (event.target === editBoatModal) editBoatModal.style.display = 'none';
    if (event.target === addTripModal) addTripModal.style.display = 'none';
    if (event.target === editTripModal) editTripModal.style.display = 'none';
}
// ========== LOAD BOATS FOR ADMIN DROPDOWN ==========
async function loadBoatsForAdmin() {
    try {
        const response = await fetch('/api/admin/boats');
        const boats = await response.json();
        
        // For Add Trip Modal
        const addSelect = document.getElementById('adminTripBoatId');
        if (addSelect) {
            addSelect.innerHTML = '<option value="">Select a boat</option>' + 
                boats.map(b => `<option value="${b.id}">${b.name} (${b.capacity} seats)</option>`).join('');
        }
        
        // For Edit Trip Modal
        const editSelect = document.getElementById('editTripBoatId');
        if (editSelect) {
            editSelect.innerHTML = '<option value="">Select a boat</option>' + 
                boats.map(b => `<option value="${b.id}">${b.name} (${b.capacity} seats)</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading boats:', error);
    }
}

// ========== ADD TRIP (ADMIN) ==========
function showAddTripModal() {
    loadBoatsForAdmin();
    document.getElementById('addTripModalAdmin').style.display = 'flex';
}

function closeAddTripModalAdmin() {
    document.getElementById('addTripModalAdmin').style.display = 'none';
}

async function addAdminTrip(event) {
    event.preventDefault();
    
    const data = {
        boat_id: document.getElementById('adminTripBoatId').value,
        from_port: document.getElementById('adminTripFrom').value,
        to_port: document.getElementById('adminTripTo').value,
        departure_date: document.getElementById('adminTripDate').value,
        departure_time: document.getElementById('adminTripTime').value,
        price: document.getElementById('adminTripPrice').value,
        available_seats: document.getElementById('adminTripSeats').value
    };
    
    if (data.from_port === data.to_port) {
        alert('Departure and destination cannot be the same!');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/trips', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            alert('Trip added successfully!');
            closeAddTripModalAdmin();
            loadTrips();
            loadDashboard();
            document.getElementById('addTripFormAdmin').reset();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error adding trip:', error);
        alert('Failed to add trip');
    }
}

// ========== EDIT TRIP (ADMIN) ==========
function openEditTripModal(trip) {
    document.getElementById('editTripId').value = trip.id;
    document.getElementById('editTripBoatId').value = trip.boat_id;
    document.getElementById('editTripFrom').value = trip.from_port;
    document.getElementById('editTripTo').value = trip.to_port;
    document.getElementById('editTripDate').value = trip.departure_date;
    document.getElementById('editTripTime').value = trip.departure_time;
    document.getElementById('editTripPrice').value = trip.price;
    document.getElementById('editTripSeats').value = trip.available_seats;
    loadBoatsForAdmin();
    document.getElementById('editTripModalAdmin').style.display = 'flex';
}

function closeEditTripModalAdmin() {
    document.getElementById('editTripModalAdmin').style.display = 'none';
}

async function updateAdminTrip(event) {
    event.preventDefault();
    
    const id = document.getElementById('editTripId').value;
    const data = {
        boat_id: document.getElementById('editTripBoatId').value,
        from_port: document.getElementById('editTripFrom').value,
        to_port: document.getElementById('editTripTo').value,
        departure_date: document.getElementById('editTripDate').value,
        departure_time: document.getElementById('editTripTime').value,
        price: document.getElementById('editTripPrice').value,
        available_seats: document.getElementById('editTripSeats').value
    };
    
    try {
        const response = await fetch(`/api/admin/trips/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        
        if (result.success) {
            alert('Trip updated successfully!');
            closeEditTripModalAdmin();
            loadTrips();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating trip:', error);
        alert('Failed to update trip');
    }
}

// ========== ADD BOAT (ADMIN) ==========
function openAddBoatModalAdmin() {
    document.getElementById('addBoatModalAdmin').style.display = 'flex';
}

function closeAddBoatModalAdmin() {
    document.getElementById('addBoatModalAdmin').style.display = 'none';
}

async function addAdminBoat(event) {
    event.preventDefault();
    
    const name = document.getElementById('adminBoatName').value;
    const capacity = document.getElementById('adminBoatCapacity').value;
    const status = document.getElementById('adminBoatStatus').value;
    
    try {
        const response = await fetch('/api/admin/boats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, capacity, status })
        });
        const result = await response.json();
        
        if (result.success) {
            alert('Boat added successfully!');
            closeAddBoatModalAdmin();
            document.getElementById('addBoatFormAdmin').reset();
            loadBoats();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error adding boat:', error);
        alert('Failed to add boat');
    }
}

// ========== EDIT BOAT (ADMIN) ==========
function openEditBoatModalAdmin(boatId, name, capacity, status) {
    document.getElementById('editBoatIdAdmin').value = boatId;
    document.getElementById('editBoatNameAdmin').value = name;
    document.getElementById('editBoatCapacityAdmin').value = capacity;
    document.getElementById('editBoatStatusAdmin').value = status;
    document.getElementById('editBoatModalAdmin').style.display = 'flex';
}

function closeEditBoatModalAdmin() {
    document.getElementById('editBoatModalAdmin').style.display = 'none';
}

async function updateAdminBoat(event) {
    event.preventDefault();
    
    const id = document.getElementById('editBoatIdAdmin').value;
    const name = document.getElementById('editBoatNameAdmin').value;
    const capacity = document.getElementById('editBoatCapacityAdmin').value;
    const status = document.getElementById('editBoatStatusAdmin').value;
    
    try {
        const response = await fetch(`/api/admin/boats/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, capacity, status })
        });
        const result = await response.json();
        
        if (result.success) {
            alert('Boat updated successfully!');
            closeEditBoatModalAdmin();
            loadBoats();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating boat:', error);
        alert('Failed to update boat');
    }
}

// Initialize
checkAuth();