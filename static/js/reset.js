// Reset Password JavaScript

const urlParams = new URLSearchParams(window.location.search);
const token = urlParams.get('token');

async function resetPassword(event) {
    event.preventDefault();
    
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const messageDiv = document.getElementById('message');
    
    messageDiv.className = 'message';
    
    if (newPassword !== confirmPassword) {
        messageDiv.textContent = 'Passwords do not match!';
        messageDiv.className = 'message error';
        return;
    }
    
    if (newPassword.length < 6) {
        messageDiv.textContent = 'Password must be at least 6 characters!';
        messageDiv.className = 'message error';
        return;
    }
    
    try {
        const response = await fetch('/api/reset-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: token, new_password: newPassword })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.className = 'message success';
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            messageDiv.textContent = data.message;
            messageDiv.className = 'message error';
        }
    } catch (error) {
        messageDiv.textContent = 'Something went wrong. Please try again.';
        messageDiv.className = 'message error';
    }
}