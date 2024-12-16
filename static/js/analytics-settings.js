// static/js/analytics-settings.js

document.addEventListener('DOMContentLoaded', function() {
    // Manipulador para o formulário de configurações gerais
    const generalForm = document.querySelector('form[name="general"]');
    if (generalForm) {
        generalForm.addEventListener('submit', function(e) {
            const trackingEnabled = document.getElementById('tracking_enabled').value;
            const dataRetention = document.getElementById('data_retention').value;

            // Validação básica
            if (!dataRetention || dataRetention < 1) {
                e.preventDefault();
                alert('Por favor, selecione um período válido de retenção de dados.');
                return false;
            }
        });
    }

    // Manipulador para o formulário de notificações
    const notificationForm = document.querySelector('form[name="notifications"]');
    if (notificationForm) {
        notificationForm.addEventListener('submit', function(e) {
            const alertThreshold = document.getElementById('alert_threshold').value;
            const notificationEmail = document.getElementById('notification_email').value;

            // Validação do email
            if (document.getElementById('daily_report').value === '1' &&
                (!notificationEmail || !notificationEmail.includes('@'))) {
                e.preventDefault();
                alert('Por favor, forneça um endereço de email válido para as notificações.');
                return false;
            }

            // Validação do limite de alerta
            if (!alertThreshold || alertThreshold < 1) {
                e.preventDefault();
                alert('Por favor, forneça um limite válido para alertas.');
                return false;
            }
        });
    }

    // Manipulador para alterações no status do tracking
    const trackingSelect = document.getElementById('tracking_enabled');
    if (trackingSelect) {
        trackingSelect.addEventListener('change', function() {
            if (this.value === '0') {
                if (!confirm('Desativar o rastreamento interromperá a coleta de dados. Tem certeza?')) {
                    this.value = '1';
                }
            }
        });
    }
});
