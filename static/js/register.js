// static/js/register.js

document.addEventListener('DOMContentLoaded', function() {
    // Função para alternar visibilidade da senha
    function togglePasswordVisibility(inputId, buttonId) {
        const input = document.getElementById(inputId);
        const button = document.getElementById(buttonId);
        const icon = button.querySelector('i');

        button.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('bi-eye');
                icon.classList.add('bi-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('bi-eye-slash');
                icon.classList.add('bi-eye');
            }
        });
    }

    // Verificação de força da senha
    function checkPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[a-z]+/)) strength++;
        if (password.match(/[A-Z]+/)) strength++;
        if (password.match(/[0-9]+/)) strength++;
        if (password.match(/[!@#$%^&*(),.?":{}|<>]+/)) strength++;
        return strength;
    }

    // Atualiza o indicador de força da senha
    function updatePasswordStrength(password) {
        const strengthDiv = document.getElementById('password-strength');
        const strength = checkPasswordStrength(password);
        let strengthText = '';
        let strengthColor = '';

        switch(strength) {
            case 0:
            case 1:
                strengthText = 'Fraca';
                strengthColor = '#dc3545';
                break;
            case 2:
            case 3:
                strengthText = 'Média';
                strengthColor = '#ffc107';
                break;
            case 4:
            case 5:
                strengthText = 'Forte';
                strengthColor = '#28a745';
                break;
        }

        strengthDiv.innerHTML = `Força da senha: <span style="color: ${strengthColor}">${strengthText}</span>`;
    }

    // Verificação de username em tempo real
    let usernameTimeout;
    const usernameInput = document.getElementById('id_username');

    usernameInput.addEventListener('input', function() {
        clearTimeout(usernameTimeout);
        const username = this.value;

        usernameTimeout = setTimeout(() => {
            if (username.length >= 3) {
                fetch(`/check-username/?username=${username}`)
                    .then(response => response.json())
                    .then(data => {
                        const feedback = this.nextElementSibling;
                        if (data.available) {
                            this.classList.remove('is-invalid');
                            this.classList.add('is-valid');
                            feedback.textContent = 'Nome de usuário disponível!';
                            feedback.className = 'valid-feedback';
                        } else {
                            this.classList.remove('is-valid');
                            this.classList.add('is-invalid');
                            feedback.textContent = 'Este nome de usuário já está em uso.';
                            feedback.className = 'invalid-feedback';
                        }
                    });
            }
        }, 500);
    });

    // Inicializa os toggles de senha
    togglePasswordVisibility('id_password1', 'togglePassword1');
    togglePasswordVisibility('id_password2', 'togglePassword2');

    // Monitor de força da senha
    document.getElementById('id_password1').addEventListener('input', function() {
        updatePasswordStrength(this.value);
    });
});