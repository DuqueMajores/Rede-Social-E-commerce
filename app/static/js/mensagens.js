document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchUserInput');
    const users = document.querySelectorAll('.chat-user-wrapper');

    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();

        users.forEach(user => {
            const username = user.getAttribute('data-username'); // Corrigido aqui
            if (username.includes(query)) {
                user.style.display = 'flex';  // Mantém a exibição adequada ao layout
            } else {
                user.style.display = 'none';
            }
        });
    });
});