function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-PH');
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PH', { style: 'currency', currency: 'PHP' }).format(amount);
}

function logout() {
    // Call logout API
    fetch('/api/logout', { method: 'POST' })
        .then(() => {
            // Clear session storage
            sessionStorage.removeItem('currentUser');
            sessionStorage.clear();
            
            // Redirect to login
            window.location.href = '/login';
        });
}

// Prevent back button after logout
function preventBackAfterLogout() {
    window.history.pushState(null, "", window.location.href);
    window.onpopstate = function() {
        window.history.pushState(null, "", window.location.href);
    };
}

// Clear cache para dili ma-store ang pages
function clearCache() {
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            window.location.reload();
        }
    });
}

// Check if user is logged in (sa pages nga need ug login)
function checkAuthForPage() {
    const currentUser = sessionStorage.getItem('currentUser');
    const publicPages = ['/login', '/register', '/forgot-password'];
    const currentPath = window.location.pathname;
    
    // If wala naka-login and wala sa public page, redirect to login
    if (!currentUser && !publicPages.includes(currentPath)) {
        window.location.href = '/login';
    }
}