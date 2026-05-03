// ============================================
// SEACLOUD - REGISTER PAGE JAVASCRIPT
// ============================================

function clearErrors() {
    document.getElementById('email-error').textContent = '';
    document.getElementById('phone-error').textContent = '';
    document.getElementById('password-error').textContent = '';
    document.getElementById('confirm-error').textContent = '';
    document.getElementById('reg-email').classList.remove('error-border');
    document.getElementById('reg-phone').classList.remove('error-border');
    document.getElementById('reg-password').classList.remove('error-border');
    document.getElementById('reg-confirm-password').classList.remove('error-border');
}

function showMessage(msg, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = msg;
    messageDiv.className = `message ${type}`;
    setTimeout(() => {
        messageDiv.className = 'message';
    }, 3000);
}

function validatePhone(phone) {
    if (!phone) return true;
    const phoneRegex = /^[0-9]{11}$/;
    return phoneRegex.test(phone);
}

async function handleRegister(event) {
    event.preventDefault();
    
    clearErrors();
    
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const phone = document.getElementById('reg-phone').value;
    const role = document.getElementById('reg-role').value;
    const password = document.getElementById('reg-password').value;
    const confirmPassword = document.getElementById('reg-confirm-password').value;
    
    let hasError = false;
    
    if (phone && !validatePhone(phone)) {
        document.getElementById('phone-error').textContent = 'Phone number must be exactly 11 digits';
        document.getElementById('reg-phone').classList.add('error-border');
        hasError = true;
    }
    
    if (password !== confirmPassword) {
        document.getElementById('confirm-error').textContent = 'Passwords do not match!';
        document.getElementById('reg-confirm-password').classList.add('error-border');
        document.getElementById('reg-password').classList.add('error-border');
        hasError = true;
    }
    
    if (password.length < 6) {
        document.getElementById('password-error').textContent = 'Password must be at least 6 characters!';
        document.getElementById('reg-password').classList.add('error-border');
        hasError = true;
    }
    
    if (hasError) return;
    
    // Check if email exists
    try {
        const checkResponse = await fetch(`/api/check_email?email=${encodeURIComponent(email)}`);
        const checkData = await checkResponse.json();
        
        if (checkData.exists) {
            document.getElementById('email-error').textContent = 'Email already registered!';
            document.getElementById('reg-email').classList.add('error-border');
            return;
        }
    } catch (error) {
        console.error('Email check error:', error);
    }
    
    // Proceed with registration
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, phone, role, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Registration successful! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
        } else {
            showMessage(data.message, 'error');
        }
    } catch (error) {
        showMessage('Something went wrong. Please try again.', 'error');
    }
}