# core/views/auth_views.py
import logging
from django.contrib.auth import logout, login, get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.views import LoginView
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt


from ..forms import CustomUserCreationForm, CustomAuthenticationForm

# Configura o logger
logger = logging.getLogger(__name__)

# Obtém o modelo de usuário correto do projeto
User = get_user_model()

def register(request):
    if request.method == 'POST':
        # Log dos dados recebidos
        logger.debug(f"Dados do POST: {request.POST}")

        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                logger.info(f"Novo usuário registrado: {user.username}")

                # Se for uma requisição AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('index'),
                        'message': 'Conta criada com sucesso! Bem-vindo!'
                    })

                # Se for uma requisição normal
                messages.success(request, 'Conta criada com sucesso! Bem-vindo!')
                return redirect('index')

            except Exception as e:
                logger.error(f"Erro ao criar usuário: {str(e)}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': f'Erro ao criar conta: {str(e)}'
                    })

                messages.error(request, f'Erro ao criar conta: {str(e)}')
        else:
            logger.warning(f"Erro no formulário de registro: {form.errors}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                errors = []
                for field, field_errors in form.errors.items():
                    for error in field_errors:
                        errors.append(f'Erro no campo {field}: {error}')
                return JsonResponse({
                    'success': False,
                    'errors': errors
                })

            # Mostra todos os erros do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
                    logger.warning(f"Campo {field}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})


class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        """Chamado quando o formulário é válido"""
        # Limpa todas as mensagens anteriores
        storage = messages.get_messages(self.request)
        storage.used = True

        # Marca a sessão para evitar contagem duplicada
        self.request.session['authenticated_visit'] = True

        response = super().form_valid(form)
        self.request.session.set_expiry(0)
        logger.info(f"Login bem-sucedido para o usuário: {self.request.user.username}")
        messages.success(self.request, f'Bem-vindo, {self.request.user.username}!')
        return response

    def form_invalid(self, form):
        """Chamado quando o formulário é inválido"""
        logger.warning(f"Tentativa de login inválida: {form.errors}")
        messages.error(self.request, 'Usuário ou senha inválidos.')
        return super().form_invalid(form)

    def get_success_url(self):
        """Define para onde redirecionar após o login bem-sucedido"""
        return self.get_redirect_url() or '/'

    def get(self, request, *args, **kwargs):
        """Limpa mensagens antigas ao acessar a página de login"""
        storage = messages.get_messages(request)
        storage.used = True
        return super().get(request, *args, **kwargs)


class CustomLogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:  # Só mostra mensagem se realmente havia um usuário logado
            username = request.user.username
            logout(request)
            logger.info(f"Logout realizado para o usuário: {username}")
            messages.info(request, 'Você saiu do sistema.')
        else:
            logout(request)
        return redirect('index')


def check_username(request):
    username = request.GET.get('username', '')
    exists = User.objects.filter(username=username).exists()
    if exists:
        logger.info(f"Verificação de username: {username} já existe")
    return JsonResponse({'available': not exists})


@csrf_exempt
def auto_logout(request):
    try:
        if request.user.is_authenticated:
            username = request.user.username
            logger.warning(f"Auto logout triggered for user: {username}")
            logger.warning(f"Request META: {request.META.get('HTTP_REFERER')}")
            logout(request)
            request.session.flush()
    except Exception as e:
        logger.error(f"Erro no auto logout: {str(e)}")
    return HttpResponse(status=200)