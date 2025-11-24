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
    updateUnreadBadge();
    updateUnreadBadgeNotifications();
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
            updateUnreadBadge();
            updateUnreadBadgeNotifications();

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

document.querySelector('#video-call-submit').onclick = function (e) {
    const meetLink = 'https://meet.new';
    window.open(meetLink, '_blank');
};

function convertGoogleMeetLinks() {
    const elements = document.querySelectorAll('.message_content');

    elements.forEach(element => {
        if (element.querySelector('a') || element.closest('a')) {
            return;
        }

        const text = element.textContent || element.innerText;

        if (text.trim().startsWith('https://meet.google.com/')) {
            const anchor = document.createElement('a');
            anchor.href = text.trim();
            anchor.textContent = text.trim();
            anchor.target = '_blank';
            anchor.rel = 'noopener noreferrer';

            element.innerHTML = '';
            element.appendChild(anchor);
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    convertGoogleMeetLinks();
});

document.addEventListener('htmx:afterSwap', function () {
    convertGoogleMeetLinks();
});

document.addEventListener('htmx:load', function () {
    convertGoogleMeetLinks();
});


function handleTimeChange(input) {
    const container = input.closest('.time-input');
    const endTimeInput = container.querySelector('input[name="end_time"]');

    if (input.value) {
        const startTime = new Date(`2000-01-01T${input.value}`);
        startTime.setHours(startTime.getHours() + 1);
        const endTimeString = startTime.toTimeString().slice(0, 5);

        endTimeInput.value = endTimeString;
    }
}
function toggleEmptyDays(checkbox) {
    console.log('hi - checkbox checked:', checkbox.checked);

    const cards = document.querySelectorAll('.card.shadow-sm.border-0.p-2.col.h-auto.d-flex.flex-column.gap-2');

    cards.forEach(card => {
        const timeInputContainer = card.querySelector('.time-input-container');
        const noPeriodsText = timeInputContainer.querySelector('p.text-muted');
        const hasNoPeriods = noPeriodsText && noPeriodsText.textContent.includes('No hay periodos programados');
        if (checkbox.checked && hasNoPeriods) {
            card.classList.add('d-none');
        } else {
            card.classList.remove('d-none');
        }
    });
}

function updateUnreadBadge() {
    fetch('/unread-count/')
        .then(response => {

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const unreadCount = data.unread_count;
            updateBadgeInAside(unreadCount);
        })
        .catch(error => console.error('Error fetching unread count:', error));
}

function updateBadgeInAside(unreadCount) {
    const allLinks = document.querySelectorAll('a.btn');
    let messagesLink = null;
    allLinks.forEach(link => {
        const textSpan = link.querySelector('span.d-none.d-md-inline');
        if (textSpan && textSpan.textContent.trim() === 'Mensajes') {
            messagesLink = link;
        }
    });

    if (!messagesLink) return;
    const badgeContainer = messagesLink.querySelector('.flex-grow-1');
    if (!badgeContainer) return;
    let badgeElement = messagesLink.querySelector('.unread-badge');

    if (unreadCount > 0) {
        if (!badgeElement) {
            badgeElement = document.createElement('div');
            badgeElement.className = 'unread-badge';
            badgeElement.innerHTML = `<span class="badge text-bg-primary me-2 text-white">${unreadCount}</span>`;
            badgeContainer.parentNode.insertBefore(badgeElement, badgeContainer.nextSibling);
        } else {
            badgeElement.innerHTML = `<span class="badge text-bg-primary me-2 text-white">${unreadCount}</span>`;
        }
        badgeElement.style.display = 'block';
    } else if (badgeElement) {
        badgeElement.style.display = 'none';
    }
}

function updateUnreadBadgeNotifications() {
    console.log("Hi");
    fetch('/unread-count-notifications/')
        .then(response => {
            console.log(response);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const unreadCount = data.unread_count;
            console.log(unreadCount);
            updateBadgeInAsideNotifications(unreadCount);
        })
        .catch(error => console.error('Error fetching unread count:', error));
}

function updateBadgeInAsideNotifications(unreadCount) {
    const allLinks = document.querySelectorAll('a.btn');
    let messagesLink = null;
    allLinks.forEach(link => {
        const textSpan = link.querySelector('span.d-none.d-md-inline');
        if (textSpan && textSpan.textContent.trim() === 'Notificaciones') {
            messagesLink = link;
        }
    });

    if (!messagesLink) return;
    const badgeContainer = messagesLink.querySelector('.flex-grow-1');
    if (!badgeContainer) return;
    let badgeElement = messagesLink.querySelector('.unread-badge');

    if (unreadCount > 0) {
        if (!badgeElement) {
            badgeElement = document.createElement('div');
            badgeElement.className = 'unread-badge';
            badgeElement.innerHTML = `<span class="badge text-bg-primary me-2 text-white">${unreadCount}</span>`;
            badgeContainer.parentNode.insertBefore(badgeElement, badgeContainer.nextSibling);
        } else {
            badgeElement.innerHTML = `<span class="badge text-bg-primary me-2 text-white">${unreadCount}</span>`;
        }
        badgeElement.style.display = 'block';
    } else if (badgeElement) {
        badgeElement.style.display = 'none';
    }
}