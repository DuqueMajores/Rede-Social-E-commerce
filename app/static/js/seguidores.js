function atualizarPaginaPreservandoScroll() {
    // Salvar posição atual do scroll no sessionStorage
    sessionStorage.setItem('scrollPos', window.scrollY);
  
    // Recarregar a página
    location.reload();
  }
  
  // Ao carregar a página, restaurar a posição do scroll
  window.addEventListener('load', () => {
    const scrollPos = sessionStorage.getItem('scrollPos');
    if (scrollPos) {
      window.scrollTo(0, parseInt(scrollPos, 10));
      sessionStorage.removeItem('scrollPos');
    }
  });
  
  document.addEventListener('click', function (e) {
    const btn = e.target;
  
    // Verifica se clicou em um botão de seguir ou deixar de seguir
    if (btn.classList.contains('seguir-btn') || btn.classList.contains('deixar-seguir-btn')) {
      const userId = btn.getAttribute('data-id');
      const isSeguir = btn.classList.contains('seguir-btn');
      const url = isSeguir ? `/follow/${userId}` : `/unfollow/${userId}`;
      const novaClasse = isSeguir ? 'deixar-seguir-btn' : 'seguir-btn';
      const removerClasse = isSeguir ? 'seguir-btn' : 'deixar-seguir-btn';
      const novaCor = isSeguir ? 'btn-danger' : 'btn-success';
      const corAntiga = isSeguir ? 'btn-success' : 'btn-danger';
      const novoTexto = isSeguir ? 'Deixar de seguir' : 'Seguir';
  
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({})
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          btn.classList.remove(removerClasse, corAntiga);
          btn.classList.add(novaClasse, novaCor);
          btn.textContent = novoTexto;
  
          // Se quiser recarregar a página após o sucesso, preserve o scroll
          // atualizarPaginaPreservandoScroll();
        } else {
          alert(`Erro ao ${isSeguir ? 'seguir' : 'deixar de seguir'}`);
        }
      })
      atualizarPaginaPreservandoScroll()
    }
  });
  
  function getCSRFToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
  }
  
