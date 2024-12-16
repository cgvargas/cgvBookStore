// Arquivo: static/js/book-interaction.js

document.addEventListener('DOMContentLoaded', function() {
    // Adiciona listeners para todos os cards de livros
    const bookCards = document.querySelectorAll('.book-card');

    bookCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Previne a propagação se o clique for em botões de ação
            if (e.target.closest('.book-actions')) {
                return;
            }

            const livroId = this.dataset.livroId;
            if (livroId) {
                window.location.href = `/livros/${livroId}/detalhes/`;
            }
        });

        // Adiciona classe para indicar que é clicável
        card.classList.add('clickable');
    });
});