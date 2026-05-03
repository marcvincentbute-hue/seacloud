// ============================================
// SEACLOUD - LOGIN PAGE JAVASCRIPT
// ============================================

function showMessage(msg, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = msg;
    messageDiv.className = `message ${type}`;
    setTimeout(() => {
        messageDiv.className = 'message';
    }, 3000);
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // I-store ang user sa sessionStorage
            sessionStorage.setItem('currentUser', JSON.stringify({
                id: data.user_id,
                name: data.user_name,
                role: data.role
            }));
    
            showMessage('Login successful! Redirecting...', 'success');
            setTimeout(() => {
                if (data.role === 'admin') window.location.href = '/admin/dashboard';
                else if (data.role === 'operator') window.location.href = '/operator/dashboard';
                else window.location.href = '/customer/dashboard';
            }, 1000);
        } else {
            showMessage('Incorrect email or password!', 'error');
        }
    } catch (error) {
        showMessage('Something went wrong. Please try again.', 'error');
    }
}