const pinBtn = document.getElementById("pin_btn");
const notificacoesContainer = document.getElementById("notificacoes_container");

if (pinBtn && notificacoesContainer) {
    notificacoesContainer.style.display = "none";

    pinBtn.addEventListener("click", () => {
        notificacoesContainer.style.display = (notificacoesContainer.style.display === "none") ? "block" : "none";

        fetch("/notificacoes_lidas", { method: "POST" })
            .then(response => {
                if (response.ok) {
                    pinBtn.classList.remove("notificado");
                } else {
                    console.error("Erro ao marcar notificações como lidas:", response.status);
                }
            })
            .catch(err => console.error("Erro na requisição:", err));
    });

    setInterval(() => {
        fetch("/verificar_novas_notificacoes")
            .then(res => res.json())
            .then(data => {
                if (data.temNovas) {
                    pinBtn.classList.add("notificado");
                }
            })
            .catch(err => console.error("Erro ao verificar notificações:", err));
    }, 10000);
}

function lerNotificacao(id) {
    fetch(`/notificacao/${id}/ler`, {
        method: 'POST',
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.status);
        // Você pode atualizar o DOM para remover a notificação visualmente também
        document.getElementById('notificacao-' + id)?.remove();
    });
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".notificacao").forEach(function (el) {
        el.addEventListener("click", function () {
            const notificacaoId = el.getAttribute("data-id");

            // Remove do DOM
            el.remove();

            // Chamada opcional ao backend para marcar como lida
            fetch(`/notificacao/lida/${notificacaoId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),  // se necessário
                }
            });
        });
    });
});

// Se estiver usando CSRF (Flask-WTF)
function getCSRFToken() {
    const match = document.cookie.match(/csrf_token=([^;]+)/);
    return match ? match[1] : '';
}

