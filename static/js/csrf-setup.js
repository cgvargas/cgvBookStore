// static/js/csrf-setup.js

// Configuração do CSRF Token para requisições AJAX
(function() {
    function getCSRFToken() {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Configura o token CSRF para todas as requisições AJAX
    const token = getCSRFToken();
    if (token) {
        document.addEventListener('DOMContentLoaded', function() {
            // Configura o Fetch API para incluir o token CSRF
            const originalFetch = window.fetch;
            window.fetch = function() {
                let [resource, config] = arguments;
                if (config === undefined) {
                    config = {};
                }
                if (config.headers === undefined) {
                    config.headers = {};
                }
                config.headers['X-CSRFToken'] = token;
                return originalFetch(resource, config);
            };
        });
    }
})();