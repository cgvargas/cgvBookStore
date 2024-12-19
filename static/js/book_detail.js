// Função de utilidade para obter cookie CSRF
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Funções de utilidade para UI
function showAlert(type, message, container) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show mt-2`;
    alert.innerHTML = `
        <strong>${type === 'success' ? 'Sucesso!' : 'Erro!'}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    container.parentElement.appendChild(alert);
}

// Sistema de Exclusão
function initDeleteSystem() {
    const deleteButton = document.getElementById('confirmDelete');
    if (!deleteButton) return;

    deleteButton.addEventListener('click', function(e) {
        e.preventDefault();

        const livroId = this.getAttribute('data-livro-id');
        const spinner = this.querySelector('.spinner-border');

        if (!livroId) {
            console.error('ID do livro não encontrado');
            return;
        }

        // Desabilita o botão e mostra o spinner
        this.disabled = true;
        spinner.classList.remove('d-none');

        // Faz a requisição AJAX
        fetch(`/livros/excluir/${livroId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na resposta do servidor');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                $('#deleteModal').modal('hide');
                window.location.href = '/profile/';
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao tentar remover o livro. Por favor, tente novamente.');
        })
        .finally(() => {
            // Reabilita o botão e esconde o spinner
            this.disabled = false;
            spinner.classList.add('d-none');
        });
    });
}

// Sistema de Avaliação
function initRatingSystem() {
    const starContainer = document.querySelector('.star-rating');
    if (!starContainer) return;

    const stars = starContainer.querySelectorAll('.star-icon');
    const ratingText = document.querySelector('.rating-text');
    const saveButton = document.createElement('button');
    let currentRating = parseInt(starContainer.parentElement.dataset.rating) || 0;
    let tempRating = currentRating;
    let isStarClicked = false;

    saveButton.className = 'btn btn-primary btn-sm ms-2 save-rating-btn d-none';
    saveButton.innerHTML = '<i class="bi bi-check2"></i> Salvar';
    starContainer.parentElement.appendChild(saveButton);

    function updateStars(rating, isClick = false) {
        stars.forEach((star, index) => {
            if (index < rating) {
                star.classList.remove('bi-star');
                star.classList.add('bi-star-fill');
            } else {
                star.classList.remove('bi-star-fill');
                star.classList.add('bi-star');
            }
        });

        updateRatingStyle(rating);

        if (isClick || (tempRating !== currentRating && isStarClicked)) {
            saveButton.classList.remove('d-none');
        }
    }

    function updateRatingStyle(rating) {
        starContainer.classList.remove('rating-bad', 'rating-good', 'rating-excellent');
        if (rating > 0) {
            if (rating <= 2) {
                starContainer.classList.add('rating-bad');
                ratingText.style.color = '#dc3545';
                ratingText.textContent = 'Ruim';
            } else if (rating <= 3) {
                starContainer.classList.add('rating-good');
                ratingText.style.color = '#ffc107';
                ratingText.textContent = 'Bom';
            } else {
                starContainer.classList.add('rating-excellent');
                ratingText.style.color = '#28a745';
                ratingText.textContent = 'Excelente';
            }
        } else {
            ratingText.textContent = '';
        }
    }

    // Inicializa com a classificação existente
    updateStars(currentRating);

    // Eventos das estrelas
    stars.forEach(star => {
        star.addEventListener('mouseover', () => {
            if (!isStarClicked) {
                tempRating = parseInt(star.dataset.rating);
                updateStars(tempRating);
            }
        });

        star.addEventListener('mouseout', () => {
            if (!isStarClicked) {
                tempRating = currentRating;
                updateStars(currentRating);
            }
        });

        star.addEventListener('click', () => {
            isStarClicked = true;
            tempRating = parseInt(star.dataset.rating);
            updateStars(tempRating, true);
        });
    });

    // Salvar classificação
    saveButton.addEventListener('click', () => {
        const livroId = document.querySelector('.rating-section').dataset.livroId;

        fetch(`/livros/${livroId}/classificar/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ classificacao: tempRating })
        })
        .then(response => response.json())
        .then(data => {
            saveButton.classList.add('d-none');
            showAlert('success', 'Classificação salva com sucesso!', starContainer);
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        })
        .catch(error => {
            showAlert('danger', 'Erro ao salvar a classificação.', starContainer);
        });
    });
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa os sistemas
    initRatingSystem();
    initDeleteSystem();

    // Inicializa os modais Bootstrap
    if (typeof bootstrap !== 'undefined') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => new bootstrap.Modal(modal));
    }
});