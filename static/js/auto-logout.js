// auto-logout.js
document.addEventListener('DOMContentLoaded', function() {
    let isLoggingOut = false;

    function performLogout() {
        if (isLoggingOut) return;

        const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfTokenElement) {
            console.log('CSRF token não encontrado, logout não será executado');
            return;
        }

        isLoggingOut = true;
        const formData = new FormData();
        formData.append('csrfmiddlewaretoken', csrfTokenElement.value);

        try {
            navigator.sendBeacon('/auto-logout/', formData);
        } catch (error) {
            console.error('Erro ao executar logout:', error);
        }
    }

    // Somente executa o logout quando o usuário realmente sair da aplicação
    window.addEventListener('beforeunload', function(event) {
        // Verifica se é uma navegação interna
        if (performance.navigation.type !== 2) {
            performLogout();
        }
    });
});