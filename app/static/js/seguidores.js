document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.seguir-btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();

            const userId = this.getAttribute('data-id');
            const botaoAtual = this;

            fetch(`/seguir/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'seguido') {
                    // Substituir o botão pelo link "Ver Perfil"
                    const linkPerfil = document.createElement('a');
                    linkPerfil.href = `/home/${userId}`;
                    linkPerfil.className = 'btn btn-outline-primary';
                    linkPerfil.textContent = 'Ver Perfil';

                    botaoAtual.replaceWith(linkPerfil);

                    // Atualizar pin de notificações
                    atualizarPinNotificacoes();
                }
            })
            .catch(error => console.error('Erro ao seguir usuário:', error));
        });
    });
});

function atualizarPinNotificacoes() {
    fetch('/verificar_novas_notificacoes', {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        if(data.temNovas) {
            const pin = document.getElementById('pin-notificacoes');
            if(pin) {
                pin.style.display = 'inline-block'; // Exibe o pin
                // Opcional: atualizar contador ou animar o pin
            }
        }
    })
    .catch(error => console.error('Erro ao atualizar notificações:', error));
}

document.querySelectorAll('.seguir-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const userId = this.getAttribute('data-id');
        fetch(`/seguir/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()  // se você usa CSRF token no Flask
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Pode desabilitar o botão ou trocar o texto para "Seguindo"
                this.textContent = 'Seguindo';
                this.disabled = true;

                // Opcional: enviar evento para atualizar notificações (ex: via WebSocket, SSE ou polling)
                atualizarNotificacoes();
            } else {
                alert(data.error);
            }
        })
        .catch(error => console.error('Erro:', error));
    });
});

function getCSRFToken() {
    // Exemplo simples: pegar token do cookie ou do meta tag
    return document.querySelector('meta[name=csrf-token]').getAttribute('content');
}

// Função que atualizaria notificações, exemplo polling ou atualização manual
function atualizarNotificacoes() {
    // Pode ser uma chamada fetch para /notificacoes endpoint para atualizar a lista em home.html
}