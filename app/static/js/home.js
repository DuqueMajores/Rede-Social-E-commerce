document.addEventListener("DOMContentLoaded", () => {
    const pinBtn = document.getElementById("pin_btn");
    const notificacoesContainer = document.getElementById("notificacoes_container");

    if (!pinBtn || !notificacoesContainer) return;

    notificacoesContainer.style.display = "none";

    function carregarNotificacoes() {
        fetch("/get_notificacoes")
            .then(res => res.json())
            .then(data => {
                if (data.notificacoes && data.notificacoes.length > 0) {
                    notificacoesContainer.innerHTML = data.notificacoes.map(n => `
                        <div class="notificacao ${n.lida ? '' : 'nao-lida'}" data-id="${n.id}">
                            <span class="icon_star_home">&#9733;</span>
                            ${n.remetente ? `<strong>${n.remetente.nome}</strong>: ` : ''}${n.mensagem}
                        </div>
                    `).join('');
                } else {
                    notificacoesContainer.innerHTML = "<p>Não há notificações.</p>";
                }
            })
            .catch(err => console.error("Erro ao carregar notificações:", err));
    }

    pinBtn.addEventListener("click", (e) => {
        e.preventDefault();
        const visivel = notificacoesContainer.style.display === "block";
        notificacoesContainer.style.display = visivel ? "none" : "block";

        if (!visivel) {
            carregarNotificacoes();

            fetch("/notificacoes_lidas", { method: "POST" })
                .then(response => {
                    if (response.ok) {
                        pinBtn.classList.remove("notificado");
                    } else {
                        console.error("Erro ao marcar notificações como lidas:", response.status);
                    }
                })
                .catch(err => console.error("Erro na requisição:", err));
        }
    });

    notificacoesContainer.addEventListener("click", (e) => {
        const notificacao = e.target.closest(".notificacao");
        if (notificacao) {
            const idNotificacao = notificacao.getAttribute("data-id");
            if (idNotificacao) {
                deletarNotificacao(idNotificacao, notificacao);
            }
        }
    });

    function verificarNotificacoes() {
        fetch(`/verificar_novas_notificacoes?ts=${Date.now()}`)
            .then(res => res.json())
            .then(data => {
                if (data.temNovas) {
                    pinBtn.classList.add("notificado");
                } else {
                    pinBtn.classList.remove("notificado");
                }
            })
            .catch(err => console.error("Erro ao verificar notificações:", err));
    }

    function deletarNotificacao(id, elemento) {
        fetch(`/notificacao/delete/${id}`, {
            method: "DELETE",
        })
        .then(response => {
            if (response.ok) {
                elemento.remove();
                if (notificacoesContainer.children.length === 0) {
                    notificacoesContainer.innerHTML = "<p>Não há notificações.</p>";
                }
            } else {
                console.error("Erro ao deletar notificação:", response.status);
            }
        })
        .catch(err => console.error("Erro na requisição DELETE:", err));
    }

    verificarNotificacoes();
    setInterval(verificarNotificacoes, 10000);
});