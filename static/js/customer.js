// ============================================
// SEACLOUD - CUSTOMER DASHBOARD JAVASCRIPT
// ============================================

let currentUser = {};

// Page switching
function showPage(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(page + '-page').classList.add('active');
    if (page === 'dashboard') loadDashboard();
    if (page === 'bookings') loadBookings();
    if (page === 'profile') loadProfile();
}

// Load dashboard stats
async function loadDashboard() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        document.getElementById('welcomeName').innerHTML = `Welcome ${currentUser.name || 'User'}! 👋`;
        document.getElementById('totalBookings').textContent = stats.total || 0;
        document.getElementById('upcomingTrips').textContent = stats.upcoming || 0;
        document.getElementById('completedTrips').textContent = stats.completed || 0;
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load bookings
async function loadBookings() {
    try {
        const response = await fetch('/api/bookings');
        const bookings = await response.json();
        const tbody = document.getElementById('bookingsBody');
        
        if (bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">No bookings yet</td></tr>';
        } else {
            tbody.innerHTML = bookings.map(b => `
                <tr>
                    <td>${b.ref}${b.from}${b.to}${b.date}${b.passengers}
                    <td><span class="badge badge-success">${b.status}</span></td>
                    <td><button onclick="viewTicket('${b.ref}')" class="btn-primary" style="padding:5px 10px; font-size:12px;">🎫 View Ticket</button></td>
                    <td>
                        <button onclick="requestCancellation('${b.ref}')" class="btn-cancel" 
                                style="background:#dc3545; color:white; padding:5px 10px; border:none; border-radius:5px; cursor:pointer;">
                            ❌ Cancel
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// Load profile
function loadProfile() {
    document.getElementById('profileName').value = currentUser.name || '';
    document.getElementById('profileEmail').value = currentUser.email || '';
    document.getElementById('profilePhone').value = currentUser.phone || '';
}

// Book ticket
async function bookTicket(event) {
    event.preventDefault();
    
    const fromPort = document.getElementById('fromPort').value;
    const toPort = document.getElementById('toPort').value;
    const travelDate = document.getElementById('travelDate').value;
    const passengers = document.getElementById('passengers').value;
    const paymentMethod = document.querySelector('input[name="payment_method"]:checked')?.value || 'cash';
    
    if (!fromPort || !toPort || !travelDate) {
        alert('Please fill in all fields');
        return;
    }
    
    if (fromPort === toPort) {
        alert('Departure and destination cannot be the same!');
        return;
    }
    
    try {
        const response = await fetch(`/api/trips?from=${fromPort}&to=${toPort}&date=${travelDate}`);
        const trips = await response.json();
        
        if (trips.length === 0) {
            alert('No trips available for this route and date');
            return;
        }
        
        const bookResponse = await fetch('/api/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                trip_id: trips[0].id, 
                passengers: parseInt(passengers),
                payment_method: paymentMethod
            })
        });
        
        const result = await bookResponse.json();
        
        if (result.success) {
            alert(`Booking successful! Reference: ${result.ref}\nPayment: ${paymentMethod.toUpperCase()}`);
            showPage('bookings');
            loadBookings();
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error booking ticket:', error);
        alert('Something went wrong!');
    }
}

// Update profile
async function updateProfile(event) {
    event.preventDefault();
    
    try {
        const response = await fetch('/api/update_profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: document.getElementById('profileName').value,
                phone: document.getElementById('profilePhone').value
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Profile updated successfully!');
            currentUser.name = document.getElementById('profileName').value;
            sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
            loadDashboard();
        } else {
            alert('Error: ' + result.message);
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        alert('Something went wrong!');
    }
}

// ========== PAYMENT METHOD FUNCTIONS ==========
function selectPaymentMethod(method) {
    const selectedOpt = document.querySelector(`.payment-option[data-method="${method}"]`);
    if (selectedOpt) {
        document.querySelectorAll('.payment-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        selectedOpt.classList.add('selected');
    }
    const radioInput = document.querySelector(`input[name="payment_method"][value="${method}"]`);
    if (radioInput) {
        radioInput.checked = true;
    }
}

function initializePaymentOptions() {
    const paymentOptions = document.querySelectorAll('.payment-option');
    paymentOptions.forEach(opt => {
        opt.addEventListener('click', () => {
            const method = opt.dataset.method;
            selectPaymentMethod(method);
        });
    });
}

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/api/current_user');
        const data = await response.json();
        
        if (!data.logged_in) {
            window.location.href = '/login';
            return;
        }
        
        if (data.user.role !== 'customer') {
            window.location.href = '/login';
            return;
        }
        
        currentUser = data.user;
        sessionStorage.setItem('currentUser', JSON.stringify(currentUser));
        loadDashboard();
        initializePaymentOptions();
        
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

async function viewTicket(bookingRef) {
    try {
        const response = await fetch(`/ticket/view/${bookingRef}`);
        const ticket = await response.json();
        
        // Display QR code
        const qrContainer = document.getElementById('ticketQR');
        qrContainer.innerHTML = `<img src="data:image/png;base64,${ticket.qr_code}" width="200" height="200">`;
        
        // Display ticket details
        const detailsContainer = document.getElementById('ticketDetails');
        detailsContainer.innerHTML = `
            <p><strong>Booking Ref:</strong> ${ticket.ref}</p>
            <p><strong>Name:</strong> ${ticket.name}</p>
            <p><strong>Route:</strong> ${ticket.from} → ${ticket.to}</p>
            <p><strong>Date:</strong> ${ticket.date} at ${ticket.time}</p>
            <p><strong>Passengers:</strong> ${ticket.passengers}</p>
            <p><strong>Amount:</strong> ₱${ticket.amount}</p>
            <p><small>Booked: ${ticket.booked_date}</small></p>
        `;
        
        document.getElementById('ticketModal').style.display = 'flex';
    } catch (error) {
        alert('Error loading ticket');
    }
}

function closeTicketModal() {
    document.getElementById('ticketModal').style.display = 'none';
}

function printTicket() {
    const printContent = document.getElementById('ticketContent').innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html><head><title>SeaCloud Ticket</title>
        <style>body{font-family:Arial;padding:20px;text-align:center;}</style>
        </head><body>${printContent}</body></html>
    `);
    printWindow.print();
}


// Initialize
checkAuth();