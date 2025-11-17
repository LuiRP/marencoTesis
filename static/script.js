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
    // Close existing connection if any
    if (eventSource) {
        eventSource.close();
    }

    eventSource = new EventSource('/stream_notification/');

    eventSource.onmessage = function (event) {
        try {
            const data = JSON.parse(event.data);
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