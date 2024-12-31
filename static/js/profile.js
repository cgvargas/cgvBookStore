// ===============================
// Controlador do Slider de Livros
// ===============================
class BookSliderController {
    constructor() {
        this.sliderTypes = ['favoritos', 'lendo', 'vou_ler', 'lidos'];
        this.init();
    }

    init() {
        console.log('Inicializando sliders...');
        this.sliderTypes.forEach(type => {
            const container = document.getElementById(`${type}-container`);
            if (container) {
                console.log(`Inicializando slider: ${type}`);
                this.initializeSliderButtons(type);
                this.updateButtonStates(type);
            } else {
                console.warn(`Container não encontrado para: ${type}`);
            }
        });
    }

    initializeSliderButtons(type) {
        const container = document.getElementById(`${type}-container`);
        const prevBtn = container.parentElement.querySelector('.slider-btn.prev');
        const nextBtn = container.parentElement.querySelector('.slider-btn.next');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.slide(type, 'prev'));
        }
        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.slide(type, 'next'));
        }

        // Listener para scroll
        container.addEventListener('scroll', () => this.updateButtonStates(type));

        // Listener para redimensionamento
        window.addEventListener('resize', () => this.updateButtonStates(type));
    }

    slide(type, direction) {
        const container = document.getElementById(`${type}-container`);
        if (!container) return;

        const scrollAmount = container.clientWidth * 0.8;
        const currentScroll = container.scrollLeft;
        const newScroll = direction === 'prev'
            ? currentScroll - scrollAmount
            : currentScroll + scrollAmount;

        container.scrollTo({
            left: newScroll,
            behavior: 'smooth'
        });

        setTimeout(() => this.updateButtonStates(type), 300);
    }

    updateButtonStates(type) {
        const container = document.getElementById(`${type}-container`);
        if (!container) return;

        const prevBtn = container.parentElement.querySelector('.slider-btn.prev');
        const nextBtn = container.parentElement.querySelector('.slider-btn.next');

        if (prevBtn) {
            const canScrollPrev = container.scrollLeft > 0;
            prevBtn.disabled = !canScrollPrev;
            prevBtn.classList.toggle('disabled', !canScrollPrev);
        }

        if (nextBtn) {
            const canScrollNext = container.scrollLeft < (container.scrollWidth - container.clientWidth - 5);
            nextBtn.disabled = !canScrollNext;
            nextBtn.classList.toggle('disabled', !canScrollNext);
        }
    }
}

// ===============================
// Gerenciamento de Perfil
// ===============================

// Função para obter o CSRF token
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

// Função para mostrar alertas
function showAlert(message, type = 'success') {
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertElement.style.zIndex = '1050';
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    document.body.appendChild(alertElement);
    setTimeout(() => alertElement.remove(), 3000);
}

// Setup do upload de foto
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

// Setup da edição de perfil
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
                const editProfileModal = bootstrap.Modal.getInstance(document.getElementById('editProfileModal'));
                if (editProfileModal) {
                    editProfileModal.hide();
                }
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

// ===============================
// Inicialização
// ===============================
document.addEventListener('DOMContentLoaded', function() {
    console.log('Inicializando página de perfil...');

    // Inicializar o controlador do slider
    window.bookSliderController = new BookSliderController();

    // Setup das funcionalidades do perfil
    setupPhotoUpload();
    setupProfileEdit();

    // Inicializar todos os tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    console.log('Inicialização concluída');
});