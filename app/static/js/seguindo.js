function atualizarPaginaPreservandoScroll() {
    // Salvar posição atual do scroll no localStorage ou sessionStorage
    sessionStorage.setItem('scrollPos', window.scrollY);
  
    // Recarregar a página
    location.reload();
  }
  
  // Ao carregar a página, restaurar a posição do scroll
  window.addEventListener('load', () => {
    const scrollPos = sessionStorage.getItem('scrollPos');
    if (scrollPos) {
      window.scrollTo(0, parseInt(scrollPos));
      sessionStorage.removeItem('scrollPos');
    }
  });

document.addEventListener("DOMContentLoaded", function () {
    const forms = document.querySelectorAll(".follow-toggle-form");

    forms.forEach(form => {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const userId = this.dataset.userId;
            const action = this.dataset.action;

            fetch(`/${action}/${userId}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'include'  // importante para manter sessão
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'seguido') {
                    this.dataset.action = 'deixar_de_seguir';
                    this.querySelector('button').textContent = 'Deixar de seguir';
                    this.querySelector('button').classList.remove('btn-primary');
                    this.querySelector('button').classList.add('btn-danger');
                } else if (data.status === 'removido') {
                    this.dataset.action = 'seguir';
                    this.querySelector('button').textContent = 'Seguir';
                    this.querySelector('button').classList.remove('btn-danger');
                    this.querySelector('button').classList.add('btn-primary');
                }
            })
            atualizarPaginaPreservandoScroll()
        });
    });
});