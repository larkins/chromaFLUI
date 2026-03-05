document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('createModal') || document.getElementById('addModal');
    if (modal) {
        window.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
});
