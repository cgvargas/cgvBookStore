// ===============================
// Funções Globais
// ===============================

window.slideBooks = function(containerId, direction) {
    const container = document.getElementById(`${containerId}-container`);
    if (!container) return;

    const bookWidth = 170;
    const visibleBooks = 4;
    const scrollAmount = bookWidth * visibleBooks;

    if (direction === 'prev') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }
}

window.getCookie = function(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===============================
// Gerenciamento de Prateleiras
// ===============================

// Variável global para o modal
window.shelfModal = null;

// Abrir gerenciador de prateleira
function openShelfManager(shelfType) {
    const modalElement = document.getElementById('shelfModal');
    if (!modalElement) {
        console.error('Modal element not found');
        return;
    }

    if (!window.shelfModal) {
        window.shelfModal = new bootstrap.Modal(modalElement);
    }

    if (window.shelfManager) {
        window.shelfManager.openShelfManager(shelfType);
    } else {
        console.error('Shelf manager not initialized');
    }
}

// Fechar gerenciador
function closeShelfManager() {
    if (window.shelfModal) {
        window.shelfModal.hide();
    }
}

// ===============================
// Event Listeners
// ===============================

function setupEventListeners() {
    let livroAtual = null;
    const transferModalElement = document.getElementById('transferModal');
    let transferModal = null;

    if (transferModalElement) {
        transferModal = new bootstrap.Modal(transferModalElement);
    }

    // Evento para excluir livro
    document.querySelectorAll('.excluir-livro-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const livroId = this.dataset.livroId;

            if (confirm('Tem certeza que deseja excluir este livro?')) {
                fetch(`/livros/excluir/${livroId}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json'
                    },
                    credentials: 'same-origin'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        throw new Error(data.message || 'Erro ao excluir livro');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    showAlert('Erro ao excluir o livro. Por favor, tente novamente.', 'error');
                });
            }
        });
    });

    // Evento para transferência
    document.querySelectorAll('.transferir-livro-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!transferModal) return;

            livroAtual = {
                id: this.dataset.livroId,
                titulo: this.dataset.livroTitulo,
                tipoAtual: this.dataset.tipoAtual
            };

            const tituloElement = document.getElementById('livroTitulo');
            if (tituloElement) {
                tituloElement.textContent = livroAtual.titulo;
            }

            document.querySelectorAll('.transferir-para').forEach(btn => {
                btn.style.display = btn.dataset.tipo === livroAtual.tipoAtual ? 'none' : 'block';
            });

            transferModal.show();
        });
    });

    // Realizar transferência
    document.querySelectorAll('.transferir-para').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!livroAtual) return;

            const novoTipo = this.dataset.tipo;
            const formData = new FormData();
            formData.append('novo_tipo', novoTipo);

            fetch(`/livros/transferir/${livroAtual.id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    if (transferModal) {
                        transferModal.hide();
                    }
                    location.reload();
                } else {
                    throw new Error(data.message || 'Erro ao transferir livro');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showAlert('Erro ao transferir o livro. Por favor, tente novamente.', 'error');
            });
        });
    });
}

// ===============================
// Sistema de Recomendações
// ===============================

class RecommendationManager {
    constructor() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refreshRecommendations');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshRecommendations());
        }

        document.querySelectorAll('.recommendation-card').forEach(card => {
            card.addEventListener('click', (e) => this.handleRecommendationClick(e));
        });
    }

    async refreshRecommendations() {
        const btn = document.getElementById('refreshRecommendations');
        if (!btn) return;

        const icon = btn.querySelector('i');

        try {
            icon.classList.add('refreshing');
            btn.disabled = true;

            await fetch('/api/preferencias/atualizar/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            });

            const response = await fetch('/api/recomendacoes/obter/');
            const data = await response.json();

            if (data.status === 'success') {
                this.updateRecommendationsUI(data.recomendacoes);
            }
        } catch (error) {
            console.error('Erro ao atualizar recomendações:', error);
            showAlert('Erro ao atualizar recomendações', 'error');
        } finally {
            if (icon) icon.classList.remove('refreshing');
            btn.disabled = false;
        }
    }

    updateRecommendationsUI(recomendacoes) {
        const container = document.getElementById('recomendacoes-container');
        if (!container) return;

        container.innerHTML = recomendacoes.length ?
            recomendacoes.map(livro => this.createRecommendationCard(livro)).join('') :
            this.createEmptyState();
    }

    createRecommendationCard(livro) {
        return `
            <div class="book-card recommendation-card" data-livro-id="${livro.id}" onclick="window.recommendationManager.handleRecommendationClick(event)" style="cursor: pointer;">
                <div class="card border-0 bg-transparent">
                    <div class="position-relative">
                        <img src="${livro.capa}"
                             alt="${livro.titulo}"
                             loading="lazy"
                             onerror="this.src='/static/images/capa-indisponivel.svg'"
                             class="book-cover">
                        <div class="recommendation-score">
                            <span class="badge bg-warning">
                                <i class="bi bi-star-fill"></i>
                                ${Number(livro.score).toFixed(1)}
                            </span>
                        </div>
                    </div>
                    <div class="card-body p-2">
                        <h6 class="card-title small mb-0 text-truncate">${livro.titulo}</h6>
                        <p class="card-text small text-muted text-truncate">${livro.autor}</p>
                        <div class="recommendation-reasons small">
                            ${livro.categoria_match ? '<span class="badge bg-info me-1">Categoria Similar</span>' : ''}
                            ${livro.autor_match ? '<span class="badge bg-success me-1">Mesmo Autor</span>' : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    createEmptyState() {
        return `
            <div class="text-center py-4">
                <i class="bi bi-emoji-smile fs-3 text-muted"></i>
                <p class="text-muted mt-2">Adicione mais livros às suas estantes para receber recomendações personalizadas!</p>
            </div>
        `;
    }

    handleRecommendationClick(e) {
        const card = e.currentTarget;
        const livroId = card.dataset.livroId;
        if (livroId) {
            window.location.href = `/livros/google/${livroId}/`;  // URL correta
        }
    }
}

// ===============================
// Funções Auxiliares
// ===============================

// Mostrar alertas
function showAlert(message, type = 'success') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertElement.style.zIndex = '1050';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
    `;

    document.body.appendChild(alertElement);

    setTimeout(() => {
        alertElement.remove();
    }, 3000);
}

// Setup do perfil
function setupProfileEdit() {
    const editProfileForm = document.getElementById('editProfileForm');
    if (!editProfileForm) return;

    editProfileForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const submitButton = editProfileForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Salvando...';

        fetch('/profile/update/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.user) {
                    document.querySelector('.profile-name').textContent = data.user.nome_completo;
                    document.querySelector('.profile-username').textContent = '@' + data.user.username;
                }

                showAlert('Perfil atualizado com sucesso!', 'success');
                $('#editProfileModal').modal('hide');

                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                throw new Error(data.message || 'Erro ao atualizar perfil');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showAlert('Erro ao atualizar o perfil', 'error');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        });
    });
}

// Setup de foto
function setupPhotoUpload() {
    const avatarInput = document.getElementById('avatarInput');
    const avatarForm = document.getElementById('avatarForm');

    if (avatarInput && avatarForm) {
        avatarInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (!file) return;

            if (file.size > 5 * 1024 * 1024) {
                showAlert('A imagem deve ter no máximo 5MB', 'error');
                return;
            }

            if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
                showAlert('Formato não suportado. Use JPG, PNG ou GIF', 'error');
                return;
            }

            const formData = new FormData();
            formData.append('profile_photo', file);
            formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

            const button = avatarForm.querySelector('.change-avatar-btn');
            const originalContent = button.innerHTML;
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';

            fetch('/profile/update-photo/', {
                method: 'POST',
                body: formData,
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    throw new Error(data.message || 'Erro ao atualizar foto');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showAlert('Erro ao atualizar foto', 'error');
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = originalContent;
            });
        });
    }
}

// ===============================
// Inicialização
// ===============================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Iniciando sistema...');

    // Inicializa recomendações
    window.recommendationManager = new RecommendationManager();

    // Inicializa modais
    document.querySelectorAll('.modal').forEach(modalElement => {
        new bootstrap.Modal(modalElement);
    });

    // Setup das funcionalidades
    setupProfileEdit();
    setupEventListeners();
    setupPhotoUpload();

    console.log('Sistema iniciado com sucesso');
});
