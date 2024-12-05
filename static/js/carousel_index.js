function slideBooks(containerId, direction) {
    const container = document.getElementById(`${containerId}-container`);
    const scrollAmount = 200; // Ajuste este valor conforme necessário

    if (direction === 'prev') {
        container.scrollLeft -= scrollAmount;
    } else {
        container.scrollLeft += scrollAmount;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    ['destaque', 'vendidos'].forEach(containerId => {
        const container = document.getElementById(`${containerId}-container`);
        const prevBtn = container.parentElement.querySelector('.prev');
        const nextBtn = container.parentElement.querySelector('.next');

        // Verifica se há overflow
        if (container.scrollWidth <= container.clientWidth) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        }

        // Atualiza visibilidade dos botões ao rolar
        container.addEventListener('scroll', () => {
            prevBtn.style.opacity = container.scrollLeft <= 0 ? '0.5' : '1';
            nextBtn.style.opacity =
                container.scrollLeft >= container.scrollWidth - container.clientWidth
                ? '0.5' : '1';
        });
    });
});