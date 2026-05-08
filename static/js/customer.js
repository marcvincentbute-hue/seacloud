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
    if (page === 'myreservations') loadMyReservations();
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

async function loadBookings() {
    try {
        const response = await fetch('/api/bookings');
        const bookings = await response.json();
        
        const tbody = document.getElementById('bookingsBody');
        
        if (!bookings || bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 40px;">No bookings yet</td></tr>';
        } else {
            tbody.innerHTML = bookings.map(b => `
                <tr>
                    <td style="padding: 12px;">${b.ref || 'N/A'}</td>
                    <td style="padding: 12px;">${b.from || 'N/A'}</td>
                    <td style="padding: 12px;">${b.to || 'N/A'}</td>
                    <td style="padding: 12px;">${b.date || 'N/A'}</td>
                    <td style="padding: 12px;">${b.passengers || 0}</td>
                    <td style="padding: 12px;"><span class="badge ${b.status === 'confirmed' ? 'badge-success' : 'badge-warning'}">${b.status || 'pending'}</span></td>
                    <td style="padding: 12px;">
                        <button onclick="viewTicket('${b.ref}')" class="btn-primary" style="padding: 5px 10px; font-size: 12px;">View Ticket</button>
                    </td>
                </table>
            `).join('');
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (error) {
        console.error('Error loading bookings:', error);
        const tbody = document.getElementById('bookingsBody');
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 40px; color: red;">Error loading bookings</td></tr>';
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
                passengers: parseInt(passengers)
            })
        });
        
        const result = await bookResponse.json();
        
        if (result.success) {
            alert(`Booking successful! Reference: ${result.ref}`);
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

function closeTicketModal() {
    document.getElementById('ticketModal').style.display = 'none';
}

function printTicket() {
    const printContent = document.getElementById('ticketContent').innerHTML;
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
            <head>
                <title>SeaCloud Ticket - ${document.querySelector('#ticketDetails p:first-child').innerText || 'Ticket'}</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                    .ticket { border: 1px solid #ccc; padding: 20px; border-radius: 10px; max-width: 400px; margin: 0 auto; }
                    @media print {
                        body { margin: 0; padding: 0; }
                        button { display: none; }
                    }
                </style>
            </head>
            <body>
                <div class="ticket">
                    ${printContent}
                </div>
                <p style="margin-top: 20px;">Thank you for choosing SeaCloud!</p>
            </body>
        </html>
    `);
    printWindow.print();
    printWindow.close();
}

// Auto-refresh dashboard every 30 seconds (tipid sa memory)
setInterval(() => {
    if (document.getElementById('dashboard-page').classList.contains('active')) {
        loadDashboard();
        loadBookings();
    }
}, 30000);

// Load my reservations (upcoming bookings)
async function loadMyReservations() {
    try {
        const response = await fetch('/api/my-reservations');
        const reservations = await response.json();
        const container = document.getElementById('reservationsGrid');
        
        if (reservations.length === 0) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">No upcoming reservations</div>';
        } else {
            container.innerHTML = reservations.map(r => `
                <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e2e8f0;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 15px;">
                        <div style="flex: 2;">
                            <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                                <div>
                                    <p style="font-weight: bold; font-size: 16px; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0077b6" stroke-width="2">
                                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                                            <circle cx="12" cy="10" r="3"/>
                                        </svg>
                                        ${r.from} → ${r.to}
                                    </p>
                                    <p style="font-size: 12px; color: #64748b; margin-top: 4px;">${r.ref}</p>
                                </div>
                                <span class="badge ${r.status === 'confirmed' ? 'badge-success' : 'badge-warning'}" style="background: ${r.status === 'confirmed' ? '#ecfdf5' : '#fef3c7'}; color: ${r.status === 'confirmed' ? '#059669' : '#d97706'}; padding: 4px 12px; border-radius: 20px; font-size: 12px;">${r.status === 'confirmed' ? 'Confirmed' : 'Pending'}</span>
                            </div>
                            <div style="display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap;">
                                <div>
                                    <span style="font-size: 12px; color: #64748b; display: flex; align-items: center; gap: 4px;">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                                            <line x1="16" y1="2" x2="16" y2="6"/>
                                            <line x1="8" y1="2" x2="8" y2="6"/>
                                            <line x1="3" y1="10" x2="21" y2="10"/>
                                        </svg>
                                        Date
                                    </span>
                                    <br><span style="font-size: 14px;">${r.date}</span>
                                </div>
                                <div>
                                    <span style="font-size: 12px; color: #64748b; display: flex; align-items: center; gap: 4px;">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <circle cx="12" cy="12" r="10"/>
                                            <polyline points="12 6 12 12 16 14"/>
                                        </svg>
                                        Time
                                    </span>
                                    <br><span style="font-size: 14px;">${r.time}</span>
                                </div>
                                <div>
                                    <span style="font-size: 12px; color: #64748b; display: flex; align-items: center; gap: 4px;">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                                            <circle cx="12" cy="7" r="4"/>
                                            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                                            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                                        </svg>
                                        Passengers
                                    </span>
                                    <br><span style="font-size: 14px;">${r.passengers}</span>
                                </div>
                                <div>
                                    <span style="font-size: 12px; color: #64748b; display: flex; align-items: center; gap: 4px;">
                                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                            <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/>
                                            <line x1="7" y1="7" x2="7.01" y2="7"/>
                                        </svg>
                                        Fare
                                    </span>
                                    <br><span style="font-size: 14px; font-weight: bold; color: #0077b6;">₱${r.amount}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (error) {
        console.error('Error loading reservations:', error);
        const container = document.getElementById('reservationsGrid');
        if (container) container.innerHTML = '<div style="padding: 40px; text-align: center; color: #ef4444;">Error loading reservations</div>';
    }
}
    
// View Ticket Function
async function viewTicket(bookingRef) {
    try {
        const response = await fetch(`/api/booking/${bookingRef}`);
        const booking = await response.json();
        
        if (booking.error) {
            alert('Booking not found!');
            return;
        }
        
        const ticketDetails = document.getElementById('ticketDetails');
        const ticketQR = document.getElementById('ticketQR');
        
        // Generate simple QR code (text only)
        ticketQR.innerHTML = `
            <div style="background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 15px;">
                <div style="font-family: monospace; font-size: 14px; color: white; letter-spacing: 2px; text-align: center;">
                    ${booking.ref}
                </div>
            </div>
        `;
        
        ticketDetails.innerHTML = `
            <div style="text-align: left; margin-top: 15px;">
                <p><strong>Booking Reference:</strong> ${booking.ref}</p>
                <p><strong>Route:</strong> ${booking.from} → ${booking.to}</p>
                <p><strong>Date:</strong> ${booking.departure_date || booking.date}</p>
                <p><strong>Time:</strong> ${booking.time || 'N/A'}</p>
                <p><strong>Passengers:</strong> ${booking.passengers}</p>
                <p><strong>Total Amount:</strong> ₱${booking.amount}</p>
                <p><strong>Status:</strong> ${booking.status}</p>
            </div>
        `;
        
        document.getElementById('ticketModal').style.display = 'flex';
        
    } catch (error) {
        console.error('Error fetching ticket:', error);
        alert('Error loading ticket details');
    }
}
// Initialize
checkAuth();