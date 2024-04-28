const tooltipTriggerList = document.querySelectorAll('[data-bs-tt="tooltip"]');
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
