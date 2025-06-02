function confirmarExclusao() {
    if (confirm("Tem certeza que deseja excluir sua conta? Esta ação é irreversível.")) {
        window.location.href = "{{ url_for('excluir_conta', id=obj.id) }}";
    }
}