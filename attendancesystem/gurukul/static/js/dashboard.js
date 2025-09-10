// Dashboard JS

document.addEventListener('DOMContentLoaded', function() {
    // Animate progress bars
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = width; }, 500);
    });

    // Auto-hide alerts
    setTimeout(() => {
        document.querySelectorAll('.alert').forEach(alert => {
            new bootstrap.Alert(alert).close();
        });
    }, 5000);
});