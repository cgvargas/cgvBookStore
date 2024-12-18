// static/js/session_manager.js
document.addEventListener('DOMContentLoaded', function() {
    // Atualiza a sessão a cada 5 minutos se houver atividade
    let activityTimeout;
    const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutos

    function refreshSession() {
        fetch('/refresh-session/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .catch(console.error);
    }

    function resetActivityTimer() {
        clearTimeout(activityTimeout);
        activityTimeout = setTimeout(refreshSession, REFRESH_INTERVAL);
    }

    // Monitora eventos de atividade
    ['mousedown', 'keydown', 'scroll', 'touchstart'].forEach(eventType => {
        document.addEventListener(eventType, resetActivityTimer);
    });

    // Inicia o timer
    resetActivityTimer();
});