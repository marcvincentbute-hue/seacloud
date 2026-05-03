// Forgot Password JavaScript

async function handleForgotPassword(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const messageDiv = document.getElementById('message');
    
    messageDiv.className = 'message';
    messageDiv.style.display = 'none';
    
    try {
        const response = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = data.message;
            messageDiv.className = 'message success';
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                window.location.href = '/login';
            }, 3000);
        } else {
            messageDiv.textContent = data.message;
            messageDiv.className = 'message error';
            messageDiv.style.display = 'block';
        }
    } catch (error) {
        messageDiv.textContent = 'Something went wrong. Please try again.';
        messageDiv.className = 'message error';
        messageDiv.style.display = 'block';
    }
}