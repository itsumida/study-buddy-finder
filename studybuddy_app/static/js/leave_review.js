// Rating functionality
const starButtons = document.querySelectorAll('.star-button');
const ratingValue = document.getElementById('ratingValue');
const ratingText = document.getElementById('ratingText');

const ratingTexts = {
    1: 'Poor - Would not recommend',
    2: 'Fair - Below expectations',
    3: 'Good - Met expectations',
    4: 'Very Good - Exceeded expectations',
    5: 'Excellent - Outstanding study buddy!'
};

starButtons.forEach(button => {
    button.addEventListener('click', function() {
        const rating = parseInt(this.dataset.rating);
        ratingValue.value = rating;
        ratingText.textContent = ratingTexts[rating];
        
        // Update star appearances
        starButtons.forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    });

    button.addEventListener('mouseenter', function() {
        const rating = parseInt(this.dataset.rating);
        starButtons.forEach((star, index) => {
            if (index < rating) {
                star.style.color = '#ffd700';
            } else {
                star.style.color = '#e2e8f0';
            }
        });
    });
});

// Reset stars on mouse leave
document.querySelector('.rating-input').addEventListener('mouseleave', function() {
    const currentRating = parseInt(ratingValue.value) || 0;
    starButtons.forEach((star, index) => {
        if (index < currentRating) {
            star.style.color = '#ffd700';
        } else {
            star.style.color = '#e2e8f0';
        }
    });
});

// Character count
const textarea = document.querySelector('textarea');
const charCount = document.getElementById('charCount');

function updateCharCount() {
    const length = textarea.value.length;
    charCount.textContent = `${length}/500 characters`;
    
    if (length > 450) {
        charCount.classList.add('warning');
    } else {
        charCount.classList.remove('warning');
    }
}

textarea.addEventListener('input', updateCharCount);
updateCharCount(); // Initial count

// Form validation
document.getElementById('reviewForm').addEventListener('submit', function(e) {
const rating = ratingValue.value;
const content = textarea.value.trim();

if (!rating) {
e.preventDefault();
alert('Please select a rating before submitting your review.');
return;
}


if (content && content.length < 10) {
e.preventDefault();
alert('Please write a more detailed review (at least 10 characters).');
textarea.focus();
return;
}

// Show loading state
const submitBtn = document.getElementById('submitBtn');
submitBtn.disabled = true;
submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Submitting...';
});


// Auto-dismiss alerts
document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
});