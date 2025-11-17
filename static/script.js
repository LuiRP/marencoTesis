const toasts = document.querySelectorAll('.toast');
toasts.forEach(toast => {
    const el = new bootstrap.Toast(toast);
    el.show();
});

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

let eventSource;

document.addEventListener('DOMContentLoaded', function () {
    startSSE();
});

function startSSE() {
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('/stream_notification/');

    eventSource.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
            refreshChatContainer();
            refreshInboxContent();

            if (data.html) {
                addToastFromHTML(data.html);

            }
        } catch (e) {
            console.error('Error parsing SSE data:', e);
        }
    };

    eventSource.onerror = function (event) {
        console.error('SSE error:', event);

        // Auto-reconnect after 3 seconds if connection fails
        setTimeout(() => {
            if (eventSource.readyState === EventSource.CLOSED) {
                console.log('Attempting to reconnect SSE...');
                startSSE();
            }
        }, 3000);
    };

    eventSource.onopen = function (event) {
        console.log('SSE connection established');
    };

    // Update button states if you have them
    const startBtn = document.querySelector('button[onclick="startSSE()"]');
    const stopBtn = document.querySelector('button[onclick="stopSSE()"]');

    if (startBtn) startBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = false;
}

function stopSSE() {
    if (eventSource) {
        eventSource.close();
        eventSource = null;
        console.log('SSE connection closed');
    }

    // Update button states
    const startBtn = document.querySelector('button[onclick="startSSE()"]');
    const stopBtn = document.querySelector('button[onclick="stopSSE()"]');

    if (startBtn) startBtn.disabled = false;
    if (stopBtn) stopBtn.disabled = true;
}

function addToastFromHTML(html) {
    const toastContainer = document.getElementById('toastContainer');

    // Create a temporary div to parse the HTML
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html.trim();

    const toastElement = tempDiv.firstElementChild;

    // Add unique ID to the toast element
    const toastId = 'toast-' + Date.now();
    toastElement.id = toastId;

    // Append to container
    toastContainer.appendChild(toastElement);

    // Initialize Bootstrap toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 5000 // 5 seconds
    });

    // Show the toast
    toast.show();

    // Remove toast from DOM after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        this.remove();
    });
}

// Close SSE connection when page is unloaded
window.addEventListener('beforeunload', function () {
    stopSSE();
});

function scrollToBottom() {
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    scrollToBottom();
});

document.body.addEventListener('htmx:afterSwap', function (evt) {
    if (evt.detail.target.id === 'messages-container') {
        scrollToBottom();
    }
});

function refreshChatContainer() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML and extract only the messages-container
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMessagesContainer = doc.getElementById('messages-container');

            if (newMessagesContainer) {
                const currentContainer = document.getElementById('messages-container');
                currentContainer.innerHTML = newMessagesContainer.innerHTML;
                scrollToBottom();
            }
        })
        .catch(error => console.error('Error refreshing chat:', error));
}

function mainContainer() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newMessagesContainer = doc.getElementById('messages-container');

            if (newMessagesContainer) {
                const currentContainer = document.getElementById('messages-container');
                currentContainer.innerHTML = newMessagesContainer.innerHTML;
            }
        })
        .catch(error => console.error('Error refreshing chat:', error));
}

function refreshInboxContent() {
    fetch(window.location.href)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newInboxContent = doc.getElementById('inboxContent');

            if (newInboxContent) {
                const currentInboxContent = document.getElementById('inboxContent');
                currentInboxContent.innerHTML = newInboxContent.innerHTML;
            }
        })
        .catch(error => console.error('Error refreshing inbox:', error));
}