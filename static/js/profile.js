// Função para controlar o slider
function slideBooks(containerId, direction) {
    console.log('Container ID:', containerId);
    console.log('Direction:', direction);

    const container = document.getElementById(`${containerId}-container`);
    console.log('Container found:', container);

    const bookWidth = 170;
    const visibleBooks = 4;
    const scrollAmount = bookWidth * visibleBooks;

    console.log('Current scroll position:', container.scrollLeft);
    console.log('Scroll amount:', scrollAmount);

    if (direction === 'prev') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }

    console.log('New scroll position:', container.scrollLeft);
}
// Variável global para armazenar a instância do modal
window.shelfModal = null;

// Função para abrir o gerenciador de prateleira
function openShelfManager(shelfType) {
    const modalElement = document.getElementById('shelfModal');

    if (!modalElement) {
        console.error('Modal element not found');
        return;
    }

    // Inicializa o modal se ainda não foi inicializado
    if (!window.shelfModal) {
        window.shelfModal = new bootstrap.Modal(modalElement);
    }

    // Chama a função do shelf manager
    if (window.shelfManager) {
        window.shelfManager.openShelfManager(shelfType);
    } else {
        console.error('Shelf manager not initialized');
    }
}


// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Gerenciamento de upload de foto
    const avatarInput = document.getElementById('avatarInput');
    const avatarForm = document.getElementById('avatarForm');

    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (!file) return;

            // Validações
            if (file.size > 5 * 1024 * 1024) {
                alert('A imagem deve ter no máximo 5MB');
                return;
            }

            if (!['image/jpeg', 'image/png', 'image/gif'].includes(file.type)) {
                alert('Formato não suportado. Use JPG, PNG ou GIF');
                return;
            }

            // Criar e enviar FormData
            const formData = new FormData();
            formData.append('profile_photo', file);
            formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

            // Mostrar indicador de carregamento
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
                if (data.status === 'success') {
                    location.reload();
                } else {
                    throw new Error(data.message || 'Erro ao atualizar foto');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao atualizar foto. Tente novamente.');
            })
            .finally(() => {
                button.disabled = false;
                button.innerHTML = originalContent;
            });
        });
    }
});

// Função para fechar o modal
function closeShelfManager() {
    if (shelfModal) {
        shelfModal.hide();
    }
}

// Função para configurar os event listeners
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
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    if (data.status === 'success') {
                        this.closest('.book-item').remove();
                        location.reload();
                    } else {
                        throw new Error(data.message || 'Erro ao excluir livro');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Erro ao excluir o livro. Por favor, tente novamente.');
                });
            }
        });
    });

    // Evento para abrir modal de transferência
    document.querySelectorAll('.transferir-livro-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!transferModal) {
                console.error('Transfer modal not found');
                return;
            }

            livroAtual = {
                id: this.dataset.livroId,
                titulo: this.dataset.livroTitulo,
                tipoAtual: this.dataset.tipoAtual
            };

            const tituloElement = document.getElementById('livroTitulo');
            if (tituloElement) {
                tituloElement.textContent = livroAtual.titulo;
            }

            // Atualiza visibilidade dos botões de transferência
            document.querySelectorAll('.transferir-para').forEach(btn => {
                btn.style.display = btn.dataset.tipo === livroAtual.tipoAtual ? 'none' : 'block';
            });

            transferModal.show();
        });
    });

    // Evento para realizar a transferência
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
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
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
                alert('Erro ao transferir o livro. Por favor, tente novamente.');
            });
        });
    });
}

// Função para obter o cookie CSRF
function getCookie(name) {
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

// Função para gerenciar edição do perfil
function setupProfileEdit() {
    const editProfileModal = document.getElementById('editProfileModal');
    const editProfileForm = document.getElementById('editProfileForm');

    if (!editProfileModal || !editProfileForm) {
        console.error('Elementos do modal de edição não encontrados');
        return;
    }

    editProfileForm.addEventListener('submit', function(e) {
        e.preventDefault();

        // Obtém os dados do formulário
        const formData = new FormData(this);

        // Adiciona o token CSRF
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));

        // Desabilita o botão de submit durante o envio
        const submitButton = editProfileForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="bi bi-arrow-repeat spin"></i> Salvando...';

        // Faz a requisição para atualizar o perfil
        fetch('/profile/update/', {
            method: 'POST',
            body: formData,
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                // Fecha o modal
                const bsModal = bootstrap.Modal.getInstance(editProfileModal);
                if (bsModal) {
                    bsModal.hide();
                }

                // Atualiza as informações na página
                if (data.user) {
                    document.querySelector('.profile-name').textContent = data.user.nome_completo;
                    document.querySelector('.profile-username').textContent = '@' + data.user.username;
                }

                // Mostra mensagem de sucesso
                showAlert('Perfil atualizado com sucesso!', 'success');

                // Recarrega a página para atualizar todas as informações
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                throw new Error(data.message || 'Erro ao atualizar perfil');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showAlert('Erro ao atualizar o perfil. Por favor, tente novamente.', 'error');
        })
        .finally(() => {
            // Reabilita o botão de submit
            submitButton.disabled = false;
            submitButton.innerHTML = originalButtonText;
        });
    });
}

// Função auxiliar para mostrar alertas
function showAlert(message, type = 'success') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertElement.style.zIndex = '1050';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.body.appendChild(alertElement);

    // Remove o alerta após 3 segundos
    setTimeout(() => {
        alertElement.remove();
    }, 3000);
}

// Inicializa o gerenciador de edição quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    setupProfileEdit();
});

// Preview da capa do livro
document.getElementById('coverUrl').addEventListener('input', function(e) {
    const url = e.target.value;
    const preview = document.getElementById('coverPreview');

    if (url) {
        preview.innerHTML = `<img src="${url}" alt="Prévia da capa" onerror="this.onerror=null;this.parentElement.innerHTML='<i class=\'bi bi-image\'></i><small class=\'text-muted\'>Imagem inválida</small>'">`;
    } else {
        preview.innerHTML = `
            <i class="bi bi-image"></i>
            <small class="text-muted">Prévia da Capa</small>
        `;
    }
});

// Manipulação do formulário
document.getElementById('addBookForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch('/adicionar-livro-manual/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Fechar o modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('addBookModal'));
            modal.hide();

            // Mostrar mensagem de sucesso
            alert('Livro adicionado com sucesso!');

            // Opcional: Recarregar a página ou atualizar a estante
            window.location.reload();
        } else {
            alert('Erro ao adicionar livro: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao processar a requisição');
    });
});

// Função para abrir o modal quando um livro não for encontrado
function showAddBookModal() {
    // Para Bootstrap 4
    $('#addBookModal').modal('show');
}

async function checkExistingBook(titulo, autor) {
    try {
        const response = await fetch(`/verificar-livro-existente/?titulo=${encodeURIComponent(titulo)}&autor=${encodeURIComponent(autor)}`);
        const data = await response.json();

        if (data.exists) {
            alert(`Este livro já existe na sua estante "${data.detalhes.tipo_display}" desde ${data.detalhes.data_adicao}`);
            return true;
        }
        return false;
    } catch (error) {
        console.error('Erro ao verificar livro:', error);
        return false;
    }
}