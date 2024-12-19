// static/js/auto-logout-v2.js
document.addEventListener('DOMContentLoaded', function() {
    const INACTIVITY_TIMEOUT = 86400 * 1000; // 24 horas em milissegundos
    let inactivityTimer;
    let isLoggingOut = false;

    // Ignora se estiver na página de login
    if (window.location.pathname === '/login/') {
        return;
    }

    function handleSessionExpired() {
        if (!isLoggingOut) {
            isLoggingOut = true;
            const currentPath = encodeURIComponent(window.location.pathname);
            window.location.href = `/login/?next=${currentPath}`;
        }
    }

    function resetInactivityTimer() {
        if (!isLoggingOut) {
            clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(handleSessionExpired, INACTIVITY_TIMEOUT);
        }
    }

    // Monitora eventos de atividade do usuário
    ['mousedown', 'keydown', 'mousemove', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetInactivityTimer, { passive: true });
    });

    resetInactivityTimer();

    // Intercepta respostas AJAX
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args).then(response => {
            if (response.status === 401) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return response.json().then(data => {
                        if (data.code === 'session_timeout') {
                            handleSessionExpired();
                        }
                        throw new Error('Session expired');
                    });
                }
            }
            return response;
        });
    });

    // Tratamento de fechamento do navegador
    window.addEventListener('beforeunload', function(event) {
        if (!isLoggingOut) {
            // Marca a sessão para verificação de fechamento do navegador
            fetch('/api/mark-browser-closing/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            }).catch(() => {});
        }
    });
});