document.addEventListener("DOMContentLoaded", function() {
    const hash = window.location.hash;
    if (hash) {
        const targetTab = document.querySelector(`button[data-bs-target="${hash}"]`);
        if (targetTab) { new bootstrap.Tab(targetTab).show(); }
    }
    const tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabButtons.forEach(button => {
        button.addEventListener('shown.bs.tab', (e) => {
            history.replaceState(null, null, e.target.getAttribute('data-bs-target'));
        });
    });
});