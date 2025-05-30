document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.seguir-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            const userId = this.getAttribute('data-id');
            fetch(`/seguir/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'seguido') {
                    this.classList.remove('btn-success');
                    this.classList.add('btn-outline-primary');
                    this.textContent = 'Ver Perfil';
                    this.classList.remove('seguir-btn');
                    this.outerHTML = `<a href="/home/${userId}" class="btn btn-outline-primary">Ver Perfil</a>`;
                }
            });
        });
    });
});