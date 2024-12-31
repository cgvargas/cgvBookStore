// carousel_index.js
window.slideBooks = function(containerId, direction) {
    const container = document.getElementById(`${containerId}-container`);
    if (!container) return;

    const scrollAmount = 220; // 180px (max-width do card) + 40px (gap)
    const currentScroll = container.scrollLeft;
    const newScroll = direction === 'prev' ?
        currentScroll - scrollAmount :
        currentScroll + scrollAmount;

    container.scrollTo({
        left: newScroll,
        behavior: 'smooth'
    });
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    ['destaque', 'vendidos'].forEach(containerId => {
        const container = document.getElementById(`${containerId}-container`);
        if (!container) return;

        // Atualiza estados dos botões durante o scroll
        container.addEventListener('scroll', function() {
            const prevBtn = container.parentElement.querySelector('.prev');
            const nextBtn = container.parentElement.querySelector('.next');

            if (prevBtn) {
                prevBtn.disabled = container.scrollLeft <= 0;
            }
            if (nextBtn) {
                nextBtn.disabled = container.scrollLeft >= (container.scrollWidth - container.clientWidth - 5);
            }
        });
    });
});