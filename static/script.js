const toasts = document.querySelectorAll('.toast');
toasts.forEach(toast => {
    const el = new bootstrap.Toast(toast);
    el.show();
});

const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))

