const stars = document.querySelectorAll('.star');
const ratingInput = document.getElementById('rating');

stars.forEach(star => {
    star.addEventListener('click', function() {
        const rating = this.getAttribute('data-rating');
        ratingInput.value = rating;
        
        stars.forEach(s => {
            if (s.getAttribute('data-rating') <= rating) {
                s.textContent = '★';
                s.style.color = '#ffc107';
            } else {
                s.textContent = '☆';
                s.style.color = '#cbd5e1';
            }
        });
    });
});

async function submitFeedback(event) {
    event.preventDefault();
    
    const rating = document.getElementById('rating').value;
    const name = document.getElementById('feedback-name').value;
    const email = document.getElementById('feedback-email').value;
    const message = document.getElementById('feedback-message').value;
    const messageDiv = document.getElementById('message');
    
    messageDiv.className = 'message';
    
    if (rating === '0') {
        messageDiv.textContent = 'Please select a rating!';
        messageDiv.classList.add('error');
        return;
    }
    
    if (!message) {
        messageDiv.textContent = 'Please enter your feedback!';
        messageDiv.classList.add('error');
        return;
    }
    
    try {
        const response = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rating, name, email, message })
        });
        
        const data = await response.json();
        
        if (data.success) {
            messageDiv.textContent = 'Thank you for your feedback!';
            messageDiv.classList.add('success');
            document.getElementById('feedbackForm').reset();
            ratingInput.value = '0';
            stars.forEach(s => {
                s.textContent = '☆';
                s.style.color = '#cbd5e1';
            });
        } else {
            messageDiv.textContent = data.message;
            messageDiv.classList.add('error');
        }
    } catch (error) {
        messageDiv.textContent = 'Something went wrong. Please try again.';
        messageDiv.classList.add('error');
    }
}