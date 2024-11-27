# auth_views.py
from django.contrib.auth import logout, login
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import render
from ..forms import CustomUserCreationForm, CustomAuthenticationForm
from ..models import CustomUser

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        messages.error(self.request, 'Nome de usuário ou senha inválidos.')
        return super().form_invalid(form)

class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')

    def post(self, request):
        logout(request)
        return redirect('index')

@never_cache
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registrado com sucesso!')
                return redirect('index')
            except Exception as e:
                messages.error(request, 'Erro ao realizar o registro. Por favor, tente novamente.')
        else:
            messages.error(request, 'Registro inválido. Verifique os dados informados.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def check_username(request):
    username = request.GET.get('username', '')
    is_available = not CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'available': is_available})