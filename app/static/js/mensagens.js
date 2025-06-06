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

function toggleDropdown(button) {
    const menu = button.nextElementSibling;
    menu.style.display = menu.style.display === 'block' ? 'none' : 'block';

    // Fecha qualquer outro menu aberto
    document.querySelectorAll('.dropdown-menu').forEach(el => {
        if (el !== menu) el.style.display = 'none';
    });
}

// Fecha o dropdown ao clicar fora
document.addEventListener('click', function (event) {
    if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});
