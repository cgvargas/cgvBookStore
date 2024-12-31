// book-modal-manager.js
export class BookModalManager {
    constructor() {
        this.init();
        this.isSubmitting = false;  // Flag para controlar submissões duplicadas
    }

    init() {
        this.initializeModals();
        this.setupEventListeners();
    }

    initializeModals() {
        // Inicializa todos os modais Bootstrap
        document.querySelectorAll('.modal').forEach(modalElement => {
            if (!modalElement.classList.contains('modal-initialized')) {
                new bootstrap.Modal(modalElement);
                modalElement.classList.add('modal-initialized');
            }
        });
    }

    setupEventListeners() {
        // Setup para o modal de compartilhamento
        this.setupShareModal();

        // Setup para o modal de exclusão
        this.setupDeleteModal();
    }

    setupShareModal() {
        const shareButtons = document.querySelectorAll('[data-bs-target="#shareModal"]');
        const shareModal = document.getElementById('shareModal');

        if (!shareModal) return;

        shareButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const modal = bootstrap.Modal.getInstance(shareModal) || new bootstrap.Modal(shareModal);
                modal.show();
            });
        });

        // Configurar botões de compartilhamento social
        shareModal.querySelectorAll('.social-share-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const platform = btn.dataset.platform;
                const title = encodeURIComponent(document.querySelector('h1').textContent);
                const url = encodeURIComponent(window.location.href);

                let shareUrl;
                switch(platform) {
                    case 'facebook':
                        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                        break;
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?text=${title}&url=${url}`;
                        break;
                    case 'whatsapp':
                        shareUrl = `https://api.whatsapp.com/send?text=${title} ${url}`;
                        break;
                }

                if (shareUrl) {
                    window.open(shareUrl, '_blank', 'width=600,height=400');
                }
            });
        });
    }

    setupDeleteModal() {
        const deleteButtons = document.querySelectorAll('[data-bs-target="#deleteModal"]');
        const deleteModal = document.getElementById('deleteModal');
        const deleteForm = document.getElementById('deleteForm');

        if (!deleteModal || !deleteForm) return;

        const bsDeleteModal = new bootstrap.Modal(deleteModal);

        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                bsDeleteModal.show();
            });
        });

        deleteForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Evita submissões duplicadas
            if (this.isSubmitting) return;
            this.isSubmitting = true;

            const submitButton = deleteForm.querySelector('button[type="submit"]');
            const spinner = submitButton.querySelector('.spinner-border');

            try {
                submitButton.disabled = true;
                spinner.classList.remove('d-none');

                const response = await fetch(deleteForm.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                    },
                });

                const data = await response.json();

                if (data.success) {
                    bsDeleteModal.hide();
                    window.location.href = data.redirect_url || '/profile/';
                } else {
                    throw new Error(data.message || 'Erro ao excluir o livro');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert(error.message || 'Erro ao excluir o livro. Por favor, tente novamente.');
            } finally {
                submitButton.disabled = false;
                spinner.classList.add('d-none');
                this.isSubmitting = false;
            }
        });
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    new BookModalManager();
});