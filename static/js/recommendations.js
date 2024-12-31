// static/js/recommendations.js
document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('refreshRecommendations');
    const recomendacoesContainer = document.getElementById('recomendacoes-container');

    function renderRecommendation(livro) {
        return `
            <div class="book-card recommendation-card" data-livro-id="${livro.id}">
                <a href="/livros/google/${livro.id}/" class="text-decoration-none">
                    <div class="card border-0 bg-transparent">
                        <div class="position-relative">
                            <img src="${livro.capa || '/static/images/capa-indisponivel.svg'}"
                                 alt="${livro.titulo}"
                                 loading="lazy"
                                 onerror="this.src='/static/images/capa-indisponivel.svg'"
                                 class="book-cover">
                            <div class="recommendation-score">
                                <span class="badge bg-warning">
                                    <i class="bi bi-star-fill"></i>
                                    ${livro.score.toFixed(1)}
                                </span>
                            </div>
                        </div>
                        <div class="card-body p-2">
                            <h6 class="card-title small mb-0 text-truncate text-dark">${livro.titulo}</h6>
                            <p class="card-text small text-muted text-truncate">${livro.autor}</p>
                            ${livro.categoria ?
                                `<p class="card-text small text-muted text-truncate">${livro.categoria}</p>`
                                : ''}
                        </div>
                    </div>
                </a>
            </div>
        `;
    }

    function renderEmptyState() {
        return `
            <div class="text-center py-4">
                <i class="bi bi-emoji-smile fs-3 text-muted"></i>
                <p class="text-muted mt-2">Adicione mais livros às suas estantes para receber recomendações personalizadas!</p>
            </div>
        `;
    }

    function updateRecommendations() {
        if (!refreshButton || !recomendacoesContainer) return;

        const originalContent = refreshButton.innerHTML;
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<i class="bi bi-arrow-clockwise animate-spin"></i> Atualizando...';

        // Primeiro atualiza as preferências
        fetch('/api/preferencias/atualizar/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(() => {
            // Depois busca as novas recomendações
            return fetch('/api/recomendacoes/obter/', {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success' && data.recomendacoes) {
                if (data.recomendacoes.length > 0) {
                    recomendacoesContainer.innerHTML = data.recomendacoes
                        .map(renderRecommendation)
                        .join('');
                } else {
                    recomendacoesContainer.innerHTML = renderEmptyState();
                }
                refreshButton.innerHTML = '<i class="bi bi-check-circle"></i> Atualizado!';
            } else {
                throw new Error(data.message || 'Erro ao atualizar recomendações');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            refreshButton.innerHTML = '<i class="bi bi-exclamation-circle"></i> Erro ao atualizar';
        })
        .finally(() => {
            setTimeout(() => {
                refreshButton.disabled = false;
                refreshButton.innerHTML = originalContent;
            }, 2000);
        });
    }

    // Event listener para o botão de atualizar
    if (refreshButton) {
        refreshButton.addEventListener('click', updateRecommendations);
    }

    // Atualização automática a cada 5 minutos
    if (recomendacoesContainer) {
        setInterval(updateRecommendations, 300000);
    }
});