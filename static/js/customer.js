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
    if (page === 'notifications') loadNotifications();
    if (page === 'payment') loadPaymentHistory(); 
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
        
        if (bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align:center">No bookings yet</td><｜PHYTHON｜>';
        } else {
            tbody.innerHTML = bookings.map(b => `
                <tr>
                    <td style="padding: 12px;">${b.ref}</td>
                    <td style="padding: 12px;">${b.from}</td>
                    <td style="padding: 12px;">${b.to}</td>
                    <td style="padding: 12px;">${b.date}</td>
                    <td style="padding: 12px;">${b.passengers}</td>
                    <td style="padding: 12px;"><span class="badge badge-success">${b.status}</span></td>
                    <td style="padding: 12px;">
                        <button onclick="viewTicket('${b.ref}')" class="btn-primary" style="padding: 5px 10px; font-size: 12px;">View Ticket</button>
                        <button onclick="requestCancellation('${b.ref}')" class="btn-cancel" style="background: #dc3545; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; margin-left: 5px;">Cancel</button>
                    </td>
                </td>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

// Load notifications (NEW FUNCTION)
// Load live notifications from database
async function loadNotifications() {
    try {
        const response = await fetch('/api/notifications');
        const notifications = await response.json();
        const container = document.getElementById('notifications-list');
        const badge = document.getElementById('notif-badge');
        
        if (notifications.length === 0) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">No notifications yet</div>';
            if (badge) badge.style.display = 'none';
        } else {
            const unreadCount = notifications.filter(n => !n.read).length;
            if (badge) {
                badge.textContent = unreadCount;
                badge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
            }
            container.innerHTML = notifications.map(n => `
                <div class="notification-item" style="padding: 15px; border-bottom: 1px solid #e2e8f0; display: flex; gap: 15px; align-items: flex-start; ${!n.read ? 'background: #f8fafc; cursor: pointer;' : ''}" onclick="${!n.read ? `markAsRead(${n.id})` : ''}">
                    <div style="width: 36px; height: 36px; border-radius: 10px; background: ${n.bg}; display: flex; align-items: center; justify-content: center;">
                        <i data-lucide="${n.icon}" style="width: 18px; height: 18px; color: ${n.color};"></i>
                    </div>
                    <div style="flex: 1;">
                        <p style="font-weight: 600; color: #1e293b;">${n.title}</p>
                        <p style="font-size: 14px; color: #64748b;">${n.message}</p>
                        <p style="font-size: 12px; color: #94a3b8; margin-top: 4px;">${n.time}</p>
                    </div>
                    ${!n.read ? '<span style="width: 8px; height: 8px; background: #059669; border-radius: 50%;"></span>' : ''}
                </div>
            `).join('');
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

// Mark notification as read
async function markAsRead(notifId) {
    try {
        await fetch(`/api/notifications/${notifId}/read`, { method: 'POST' });
        loadNotifications(); // Reload to update badge
        loadDashboard(); // Update badge count in sidebar
    } catch (error) {
        console.error('Error marking as read:', error);
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

// Load payment history
async function loadPaymentHistory() {
    try {
        const response = await fetch('/api/payments');
        const payments = await response.json();
        const container = document.getElementById('paymentHistoryGrid');
        
        if (payments.length === 0) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">No payment history</div>';
        } else {
            container.innerHTML = payments.map(p => `
                <div style="background: white; border-radius: 16px; padding: 16px; border: 1px solid #e2e8f0; transition: all 0.2s;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                        <div>
                            <p style="font-weight: 600; color: #1e293b;">${p.route}</p>
                            <p style="font-size: 12px; color: #64748b; margin-top: 4px;">${p.method} · ${p.date}</p>
                        </div>
                        <p style="font-size: 18px; font-weight: bold; color: #0077b6;">${p.amount}</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
                        <span class="badge ${p.status === 'paid' ? 'badge-success' : 'badge-warning'}">${p.status === 'paid' ? 'Paid ✓' : 'Pending'}</span>
                        ${p.status !== 'paid' ? '<button onclick="payNow()" class="btn-primary" style="padding: 6px 12px; font-size: 12px; width: auto;">Pay Now</button>' : ''}
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading payment history:', error);
        const container = document.getElementById('paymentHistoryGrid');
        if (container) container.innerHTML = '<div style="padding: 40px; text-align: center; color: #ef4444;">Error loading payment history</div>';
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

// Auto-refresh dashboard every 10 seconds
setInterval(() => {
    if (document.getElementById('dashboard-page').classList.contains('active')) {
        loadDashboard();
        loadBookings();
    }
}, 10000);

// Load my reservations (upcoming bookings) - Column layout
async function loadMyReservations() {
    try {
        const response = await fetch('/api/my-reservations');
        const reservations = await response.json();
        const container = document.getElementById('reservationsGrid');
        
        if (reservations.length === 0) {
            container.innerHTML = '<div style="padding: 40px; text-align: center; color: #94a3b8;">No upcoming reservations</div>';
        } else {
            container.innerHTML = reservations.map(r => `
                <div style="background: white; border-radius: 16px; padding: 20px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
                    <div style="flex: 2;">
                        <div style="display: flex; align-items: center; gap: 15px; flex-wrap: wrap;">
                            <div>
                                <p style="font-weight: bold; font-size: 16px; color: #1e293b;">${r.from} → ${r.to}</p>
                                <p style="font-size: 12px; color: #64748b; margin-top: 4px;">${r.ref}</p>
                            </div>
                            <span class="badge ${r.status === 'pending' ? 'badge-warning' : 'badge-success'}" style="background: ${r.status === 'pending' ? '#fef3c7' : '#ecfdf5'}; color: ${r.status === 'pending' ? '#d97706' : '#059669'}; padding: 4px 12px; border-radius: 20px; font-size: 12px;">${r.status === 'pending' ? 'Pending Payment' : 'Confirmed'}</span>
                        </div>
                        <div style="display: flex; gap: 20px; margin-top: 12px; flex-wrap: wrap;">
                            <div><span style="font-size: 12px; color: #64748b;">📅 Date</span><br><span style="font-size: 14px;">${r.date}</span></div>
                            <div><span style="font-size: 12px; color: #64748b;">⏰ Time</span><br><span style="font-size: 14px;">${r.time}</span></div>
                            <div><span style="font-size: 12px; color: #64748b;">👥 Passengers</span><br><span style="font-size: 14px;">${r.passengers}</span></div>
                            <div><span style="font-size: 12px; color: #64748b;">💰 Fare</span><br><span style="font-size: 14px; font-weight: bold; color: #0077b6;">₱${r.amount}</span></div>
                        </div>
                    </div>
                    <div>
                        <button onclick="requestCancellation('${r.ref}')" class="btn-cancel" style="background: #dc3545; color: white; padding: 8px 16px; border: none; border-radius: 8px; cursor: pointer; font-size: 12px;">❌ Cancel</button>
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

// Initialize
checkAuth();