document.addEventListener('DOMContentLoaded', function() {
    // Função para alternar visibilidade da senha
    function togglePasswordVisibility(inputId, buttonId) {
        const input = document.getElementById(inputId);
        const button = document.getElementById(buttonId);

        if (input && button) {
            const icon = button.querySelector('i');
            if (icon) {
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
            } else {
                console.error('Ícone não encontrado no botão.');
            }
        } else {
            console.error('Elemento de entrada ou botão não encontrado.');
        }
    }

    // Chame a função com os IDs dos elementos
    togglePasswordVisibility('id_password1', 'togglePassword1');
    togglePasswordVisibility('id_password2', 'togglePassword2');

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
        if (strengthDiv) {
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
        } else {
            console.error('Elemento de força da senha não encontrado.');
        }
    }

    // Verificação de username em tempo real
    let usernameTimeout;
    const usernameInput = document.getElementById('id_username');
    if (usernameInput) {
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
    } else {
        console.error('Elemento de entrada de username não encontrado.');
    }

    // Monitor de força da senha
    const passwordInput = document.getElementById('id_password1');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value);
        });
    } else {
        console.error('Elemento de entrada de senha não encontrado.');
    }
});
