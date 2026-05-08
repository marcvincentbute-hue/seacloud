// ============================================
// SEACLOUD - OPERATOR DASHBOARD JAVASCRIPT
// ============================================

let currentUser = {};

// ========== PAGE SWITCHING ==========
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + '-page').classList.add('active');
    if (page === 'dashboard') {
        loadDashboard();
    }
    if (page === 'boats') {
        loadBoats();
    }
    if (page === 'trips') {
        loadTrips();
        loadBoatsForDropdown();
    }
    if (page === 'bookings') loadBookings();
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
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">No boats found</td></tr>';
        } else {
            tbody.innerHTML = boats.map(b => `
                <tr>
                    <td style="padding: 12px;">${b.id}</td>
                    <td style="padding: 12px;"><strong>${b.name}</strong></td>
                    <td style="padding: 12px;">${b.capacity} seats</td>
                    <td style="padding: 12px;"><span class="badge ${b.status === 'available' ? 'badge-success' : 'badge-danger'}">${b.status}</span></td>
                    <td style="padding: 12px; white-space: nowrap;">
                        <button onclick="openEditBoatModal(${b.id}, '${b.name}', ${b.capacity}, '${b.status}')" style="background: #ffc107; color: #333; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer; margin-right: 5px;">Edit</button>
                        <button onclick="deleteBoat(${b.id})" style="background: #dc3545; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;">Delete</button>
                    </td>
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
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center">No trips found</td></tr>';
        } else {
            tbody.innerHTML = trips.map(t => `
                <tr>
                    <td style="padding: 12px;">${t.id}</td>
                    <td style="padding: 12px;">${t.boat_name || 'N/A'}</td>
                    <td style="padding: 12px;">${t.from_port}</td>
                    <td style="padding: 12px;">${t.to_port}</td>
                    <td style="padding: 12px;">${t.departure_date}</td>
                    <td style="padding: 12px;">${t.departure_time}</td>
                    <td style="padding: 12px;"><strong>₱${t.price}</strong></td>
                    <td style="padding: 12px;">${t.available_seats}</td>
                    <td style="padding: 12px;">
                        ${t.status === 'completed' 
                            ? '<span style="background: #28a745; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px;">✓ Completed</span>' 
                            : `<button onclick="completeTrip(${t.id}, this)" style="background: #0077b6; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px; border: none; cursor: pointer;">Complete</button>`
                        }
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading trips:', error);
    }
}

async function completeTrip(tripId, buttonElement) {
    if (confirm('Mark this trip as completed?')) {
        try {
            const response = await fetch(`/api/operator/trips/${tripId}/complete`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            
            if (result.success) {
                alert('Trip marked as completed!');
                // Palitan ang button ng "✓ Completed" text
                buttonElement.parentElement.innerHTML = '<span style="background: #28a745; color: white; padding: 4px 10px; font-size: 11px; border-radius: 4px;">✓ Completed</span>';
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error completing trip:', error);
            alert('Failed to complete trip');
        }
    }
}

async function loadBookings() {
    try {
        const response = await fetch('/api/operator/bookings');
        const bookings = await response.json();
        const tbody = document.getElementById('bookingsTable');
        
        if (bookings.length === 0) {
            tbody.innerHTML = '</table><td colspan="6" style="text-align:center">No bookings found</td></tr>';
        } else {
            tbody.innerHTML = bookings.map(b => `
                <tr>
                    <td style="padding: 12px;"><strong>${b.ref}</strong></td>
                    <td style="padding: 12px;">${b.customer_name}</td>
                    <td style="padding: 12px;">${b.from_port}</td>
                    <td style="padding: 12px;">${b.to_port}</td>
                    <td style="padding: 12px;">${b.departure_date}</td>
                    <td style="padding: 12px;">${b.passengers} passenger(s)</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// ========== MODAL FUNCTIONS ==========
function openAddTripModal() {
    const modal = document.getElementById('addTripModal');
    if (modal) {
        modal.style.display = 'flex';
        loadBoatsForDropdown();
    }
}

function closeAddTripModal() {
    const modal = document.getElementById('addTripModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function openAddBoatModal() {
    const modal = document.getElementById('addBoatModal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeAddBoatModal() {
    const modal = document.getElementById('addBoatModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Close modal when clicking outside
window.onclick = function(event) {
    const tripModal = document.getElementById('addTripModal');
    const boatModal = document.getElementById('addBoatModal');
    const editBoatModal = document.getElementById('editBoatModal');
    
    if (event.target === tripModal) {
        tripModal.style.display = 'none';
    }
    if (event.target === boatModal) {
        boatModal.style.display = 'none';
    }
    if (event.target === editBoatModal) {
        editBoatModal.style.display = 'none';
    }
}

// ========== DELETE FUNCTIONS ==========
async function deleteBoat(boatId) {
    if (confirm('Are you sure you want to delete this boat?')) {
        try {
            const response = await fetch(`/api/operator/boats/${boatId}`, {
                method: 'DELETE'
            });
            const result = await response.json();
            if (result.success) {
                alert('Boat deleted successfully!');
                loadBoats();
                loadDashboard();
            } else {
                alert('Error: ' + result.message);
            }
        } catch (error) {
            console.error('Error deleting boat:', error);
            alert('Failed to delete boat');
        }
    }
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

// ========== ADD BOAT FUNCTION ==========
async function addOperatorBoat(event) {
    event.preventDefault();
    
    const name = document.getElementById('newBoatName').value;
    const capacity = document.getElementById('newBoatCapacity').value;
    
    if (!name || !capacity) {
        alert('Please fill in all fields');
        return;
    }
    
    try {
        const response = await fetch('/api/operator/boats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, capacity, status: 'available' })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Boat added successfully!');
            document.getElementById('addBoatForm').reset();
            closeAddBoatModal();
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

// ========== LOAD BOATS FOR DROPDOWN ==========
async function loadBoatsForDropdown() {
    try {
        const response = await fetch('/api/operator/boats');
        const boats = await response.json();
        const select = document.getElementById('tripBoatId');
        
        if (!select) return;
        
        if (boats.length === 0) {
            select.innerHTML = '<option value="">No boats available. Add a boat first!</option>';
        } else {
            select.innerHTML = '<option value="">Select a boat</option>' + 
                boats.map(b => `<option value="${b.id}">${b.name} (${b.capacity} seats)</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading boats:', error);
    }
}

// ========== ADD TRIP FUNCTION ==========
async function addOperatorTrip(event) {
    event.preventDefault();
    
    const boat_id = document.getElementById('tripBoatId').value;
    const from_port = document.getElementById('tripFrom').value;
    const to_port = document.getElementById('tripTo').value;
    const departure_date = document.getElementById('tripDate').value;
    const departure_time = document.getElementById('tripTime').value;
    const price = document.getElementById('tripPrice').value;
    const available_seats = document.getElementById('tripSeats').value;
    
    // Validation
    if (!boat_id || !from_port || !to_port || !departure_date || !departure_time || !price || !available_seats) {
        alert('Please fill in all fields');
        return;
    }
    
    // I-check kung pareho ang from at to
    if (from_port === to_port) {
        alert('Departure and destination cannot be the same!');
        return;
    }
    
    try {
        const response = await fetch('/api/operator/trips', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                boat_id, 
                from_port, 
                to_port, 
                departure_date, 
                departure_time, 
                price, 
                available_seats 
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Trip added successfully!');
            document.getElementById('addTripForm').reset();
            closeAddTripModal();
            loadTrips();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error adding trip:', error);
        alert('Failed to add trip');
    }
}

// ========== EDIT BOAT FUNCTIONS ==========
function openEditBoatModal(boatId, name, capacity, status) {
    document.getElementById('editBoatId').value = boatId;
    document.getElementById('editBoatName').value = name;
    document.getElementById('editBoatCapacity').value = capacity;
    document.getElementById('editBoatStatus').value = status;
    document.getElementById('editBoatModal').style.display = 'flex';
}

function closeEditBoatModal() {
    document.getElementById('editBoatModal').style.display = 'none';
}

async function updateOperatorBoat(event) {
    event.preventDefault();
    
    const id = document.getElementById('editBoatId').value;
    const name = document.getElementById('editBoatName').value;
    const capacity = document.getElementById('editBoatCapacity').value;
    const status = document.getElementById('editBoatStatus').value;
    
    try {
        const response = await fetch(`/api/operator/boats/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, capacity, status })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Boat updated successfully!');
            closeEditBoatModal();
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