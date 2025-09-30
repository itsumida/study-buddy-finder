document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('messageInput');
    const charCounter = document.getElementById('charCounter');
    const sendBtn = document.getElementById('sendBtn');
    const messageForm = document.getElementById('messageForm');
    const messagesContainer = document.getElementById('messagesContainer');

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addMessageToChat(content, isSent, status = '') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isSent ? 'sent' : 'received'}`;
        messageDiv.innerHTML = `
            <div class="message-bubble">
                ${content}
                <div class="message-time">Just now</div>
                ${isSent ? `<div class="message-status">${status}</div>` : ''}
            </div>
        `;
        const emptyState = messagesContainer.querySelector('.empty-state');
        if (emptyState) emptyState.remove();
        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // Input listener
    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';

        const length = this.value.length;
        charCounter.textContent = `${length}/500`;
        charCounter.classList.toggle('warning', length > 450);

        sendBtn.disabled = length === 0 || length > 500;
    });

    // Submit handler
    messageForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const content = messageInput.value.trim();
        if (!content) return;

        sendBtn.disabled = true;
        sendBtn.classList.add('sending');
        sendBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';

        // Optimistic add
        addMessageToChat(content, true, 'Sending...');

        try {
            const response = await fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ content })
            });

            if (response.ok) {
                location.reload(); // Refresh to load updated messages from DB
            } else {
                console.error('Server error');
                sendBtn.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i>';
            }
        } catch (err) {
            console.error('Network error:', err);
            sendBtn.innerHTML = '<i class="bi bi-exclamation-triangle-fill"></i>';
        } finally {
            sendBtn.disabled = false;
            sendBtn.classList.remove('sending');
        }

        // Reset input
        messageInput.value = '';
        messageInput.style.height = 'auto';
        charCounter.textContent = '0/500';
        charCounter.classList.remove('warning');
    });

    // Enter key handling
    messageInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim()) {
                messageForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Auto-scroll on load
    scrollToBottom();
    messageInput.focus();
});
