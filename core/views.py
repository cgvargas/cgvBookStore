# core/views.py
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.contrib import  messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from bookstore import settings
from .forms import ContatoForm, CustomUserCreationForm
from .models import Livro, URLExterna, VideoYouTube
from .api import buscar_livro_google, buscar_detalhes_livro
from django.contrib.auth.views import LoginView, LogoutView


class CustomLoginView(LoginView):
    template_name = 'login.html'


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')

    def post(self, request):
        logout(request)
        return redirect('index')


def profile(request):
    return render(request, 'perfil.html')


def index(request):
    livros_destaque = Livro.objects.filter(destaque=True)
    livros_mais_vendidos = Livro.objects.filter(mais_vendido=True)
    urls_externas = URLExterna.objects.all()
    videos_youtube = VideoYouTube.objects.all()

    context = {
        'livros_destaque': livros_destaque,
        'livros_mais_vendidos': livros_mais_vendidos,
        'urls_externas': urls_externas,
        'videos_youtube': videos_youtube,
    }
    return render(request, 'index.html', context)


def sobre(request):
    return render(request, 'sobre.html')


def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST or None)
        if form.is_valid():
            form.save()
            nome = form.cleaned_data['nome']
            email_cliente = form.cleaned_data['email']  # Renomeado para clareza
            assunto = form.cleaned_data['assunto']
            mensagem = form.cleaned_data['mensagem']

            # Crie uma mensagem mais elaborada
            corpo_email = f"""
            Nova mensagem de contato recebida:

            Nome: {nome}
            Email: {email_cliente}
            Assunto: {assunto}

            Mensagem:
            {mensagem}
            """

            # Use as configurações do settings.py
            try:
                send_mail(
                    subject=f'Nova mensagem de {nome}: {assunto}',
                    message=corpo_email,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin[1] for admin in settings.ADMINS],
                    fail_silently=False,
                )
                messages.success(request, 'Mensagem enviada com sucesso!')
            except Exception as e:
                print(f"Erro ao enviar e-mail: {e}")
                messages.error(request, 'Erro ao enviar mensagem. Por favor, tente novamente mais tarde.')
    else:
        form = ContatoForm()

    context = {'form': form}
    return render(request, 'contato.html', context)


def livro_detail(request, livro_id):
    livro = get_object_or_404(Livro, pk=livro_id)
    return render(request, 'livro_detail.html', {'livro': livro})


def buscar_livro(request):
    livros_encontrados = []
    tipo_busca = request.GET.get('tipo_busca')
    query = request.GET.get('query')

    if query:
        livros_encontrados = buscar_livro_google(query, tipo_busca)

    return render(request, 'buscar_livro.html', {'livros': livros_encontrados})


def detalhe_livro(request, livro_id):
    livro = buscar_detalhes_livro(livro_id)
    return render(request, 'detalhe_livro.html', {'livro': livro})


def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')


def termos_uso(request):
    return render(request, 'termos_uso.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registrado com sucesso!')
            return redirect('index')
        else:
            messages.error(request, 'Registro inválido.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

