// shelf-manager.js
export class ShelfManager {
    constructor(modalInstance) {
        this.modal = modalInstance;
        this.currentBook = null;
        this.transferModal = null;

        // Inicializar o modal de transferência
        const transferModalElement = document.getElementById('transferModal');
        if (transferModalElement) {
            this.transferModal = new bootstrap.Modal(transferModalElement);
        }
    }

    initialize() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Eventos de exclusão
        document.querySelectorAll('.excluir-livro-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleBookDeletion(e));
        });

        // Eventos de transferência
        document.querySelectorAll('.transferir-livro-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTransferModalOpen(e));
        });

        // Botões de transferência dentro do modal
        document.querySelectorAll('.transferir-para').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleBookTransfer(e));
        });
    }

    handleBookDeletion(event) {
        event.preventDefault();
        const livroId = event.target.dataset.livroId;

        if (confirm('Tem certeza que deseja excluir este livro?')) {
            this.deleteBook(livroId);
        }
    }

    handleTransferModalOpen(event) {
        event.preventDefault();
        if (!this.transferModal) {
            console.error('Transfer modal not found');
            return;
        }

        this.currentBook = {
            id: event.target.dataset.livroId,
            titulo: event.target.dataset.livroTitulo,
            tipoAtual: event.target.dataset.tipoAtual
        };

        // Atualizar título no modal
        const tituloElement = document.getElementById('livroTitulo');
        if (tituloElement) {
            tituloElement.textContent = this.currentBook.titulo;
        }

        // Atualizar visibilidade dos botões
        document.querySelectorAll('.transferir-para').forEach(btn => {
            btn.style.display = btn.dataset.tipo === this.currentBook.tipoAtual ? 'none' : 'block';
        });

        this.transferModal.show();
    }

    handleBookTransfer(event) {
        event.preventDefault();
        if (!this.currentBook) return;

        const novoTipo = event.target.dataset.tipo;
        this.transferBook(this.currentBook.id, novoTipo);
    }

    async deleteBook(livroId) {
        try {
            const response = await fetch(`/livros/excluir/${livroId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (data.status === 'success') {
                location.reload();
            } else {
                throw new Error(data.message || 'Erro ao excluir livro');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao excluir o livro. Por favor, tente novamente.');
        }
    }

    async transferBook(livroId, novoTipo) {
        const formData = new FormData();
        formData.append('novo_tipo', novoTipo);

        try {
            const response = await fetch(`/livros/transferir/${livroId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: formData,
                credentials: 'same-origin'
            });

            const data = await response.json();

            if (data.status === 'success') {
                if (this.transferModal) {
                    this.transferModal.hide();
                }
                location.reload();
            } else {
                throw new Error(data.message || 'Erro ao transferir livro');
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao transferir o livro. Por favor, tente novamente.');
        }
    }

    getCookie(name) {
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

    openShelfManager(shelfType) {
        if (!this.modal) {
            console.error('Modal instance not found');
            return;
        }

        fetch(`/prateleira/${shelfType}/livros/`)
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    const modalElement = document.getElementById('shelfModal');
                    const modalTitle = modalElement.querySelector('.modal-title');
                    const modalBody = modalElement.querySelector('.modal-body');

                    if (modalTitle) {
                        const titles = {
                            'favorito': 'Gerenciar Favoritos',
                            'lendo': 'Gerenciar Lendo',
                            'vou_ler': 'Gerenciar Vou Ler',
                            'lido': 'Gerenciar Lidos'
                        };
                        modalTitle.textContent = titles[shelfType] || 'Gerenciar Prateleira';
                    }

                    if (modalBody) {
                        modalBody.innerHTML = data.html;
                        this.setupEventListeners();
                        this.modal.show();
                    }
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao carregar os livros. Por favor, tente novamente.');
            });
    }
}

// Função de inicialização para uso no template
export function initializeShelfManager(modalInstance) {
    const manager = new ShelfManager(modalInstance);
    manager.initialize();
    return manager;
}