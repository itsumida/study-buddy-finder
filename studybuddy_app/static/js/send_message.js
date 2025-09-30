// Character counter
const textarea = document.getElementById('content');
const charCounter = document.getElementById('charCounter');
const sendBtn = document.getElementById('sendBtn');

textarea.addEventListener('input', function() {
    const length = this.value.length;
    charCounter.textContent = `${length}/500 characters`;
    
    if (length > 450) {
        charCounter.classList.add('warning');
    } else {
        charCounter.classList.remove('warning');
    }
    
    sendBtn.disabled = length === 0 || length > 500;
});

// Form submission
document.getElementById('messageForm').addEventListener('submit', function(e) {
    const content = textarea.value.trim();
    if (!content) {
        e.preventDefault();
        alert('Please write a message before sending.');
        return;
    }

    sendBtn.disabled = true;
    sendBtn.classList.add('sending');
    sendBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Sending Message...';
});

// Set message from suggestion
function setMessage(message) {
    textarea.value = message;
    textarea.dispatchEvent(new Event('input'));
    textarea.focus();
}

// Auto-dismiss success messages
document.querySelectorAll('.success-message').forEach(message => {
    setTimeout(() => {
        message.style.opacity = '0';
        setTimeout(() => {
            message.remove();
        }, 300);
    }, 5000);
});

// Focus on textarea when page loads
document.addEventListener('DOMContentLoaded', function() {
    textarea.focus();
});