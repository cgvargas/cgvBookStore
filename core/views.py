# core/views.py
import logging
from django.contrib.auth import logout, login
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.decorators.cache import never_cache
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.templatetags.static import static

from bookstore import settings
from .forms import ContatoForm, CustomUserCreationForm, CustomAuthenticationForm
from .utils.email_utils import enviar_email_contato
from .models import Livro, URLExterna, VideoYouTube, CustomUser
from .api import google_books_api

logger = logging.getLogger(__name__)


# ==========================================
# Views de Autenticação
# ==========================================

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomAuthenticationForm

    def form_invalid(self, form):
        print(f"Login attempt - Username: {form.cleaned_data['username']}")
        messages.error(self.request, 'Nome de usuário ou senha inválidos.')
        return super().form_invalid(form)


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('index')

    def post(self, request):
        logout(request)
        return redirect('index')


@login_required
def profile(request):
    return render(request, 'perfil.html')


# ==========================================
# Views de Páginas Principais
# ==========================================

def index(request):
    try:
        context = {
            'livros_destaque': Livro.objects.filter(destaque=True),
            'livros_mais_vendidos': Livro.objects.filter(mais_vendido=True),
            'urls_externas': URLExterna.objects.all(),
            'videos_youtube': VideoYouTube.objects.all(),
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Erro na página inicial: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao carregar a página inicial.')
        return render(request, 'index.html', {})


def sobre(request):
    return render(request, 'sobre.html')


def contato(request):
    """View para o formulário de contato com resposta automática."""
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                # Salva o contato
                contato = form.save()

                # Envia os e-mails
                emails_enviados = enviar_email_contato(form.cleaned_data)

                if emails_enviados:
                    messages.success(
                        request,
                        'Mensagem enviada com sucesso! Verifique seu e-mail para confirmação.'
                    )
                else:
                    messages.warning(
                        request,
                        'Sua mensagem foi recebida, mas houve um problema ao enviar o e-mail de confirmação.'
                    )

                return redirect('contato')

            except Exception as e:
                logger.error(f"Erro no formulário de contato: {str(e)}")
                messages.error(
                    request,
                    'Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.'
                )
    else:
        form = ContatoForm()

    return render(request, 'contato.html', {'form': form})


# ==========================================
# Views de Livros Locais
# ==========================================

def livro_detail(request, livro_id):
    try:
        livro = get_object_or_404(Livro, pk=livro_id)
        livros_relacionados = Livro.objects.filter(
            destaque=True
        ).exclude(id=livro.id)[:4]

        context = {
            'livro': livro,
            'livros_relacionados': livros_relacionados,
        }
        return render(request, 'livro_detail.html', context)
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do livro local {livro_id}: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao buscar os detalhes do livro.')
        return redirect('index')


# ==========================================
# Views de Busca Google Books
# ==========================================

def buscar_livro(request):
    livros_encontrados = []
    livros_paginados = []
    tipo_busca = request.GET.get('tipo_busca', '')
    query = request.GET.get('query', '')
    order = request.GET.get('order', 'title')
    page = request.GET.get('page', 1)

    try:
        if query:
            resultados = google_books_api.buscar_livros(query, tipo_busca)
            livros_encontrados = _processar_resultados_google_books(resultados)

            if livros_encontrados:
                livros_encontrados = _ordenar_resultados(livros_encontrados, order)
                livros_paginados = _paginar_resultados(livros_encontrados, page)
            else:
                messages.info(request, 'Nenhum livro encontrado com os critérios informados.')

    except Exception as e:
        logger.error(f"Erro durante a busca: {str(e)}")
        messages.error(request, 'Ocorreu um erro durante a busca. Por favor, tente novamente.')

    context = {
        'livros': livros_paginados,
        'query': query,
        'tipo_busca': tipo_busca,
        'order': order,
        'page_obj': livros_paginados if livros_encontrados else None,
    }

    return render(request, 'buscar_livro.html', context)


def google_book_detail(request, livro_id):
    """View para exibir detalhes de um livro do Google Books."""
    try:
        logger.info(f"Buscando detalhes do livro Google ID: {livro_id}")
        livro = google_books_api.buscar_detalhes(livro_id)

        if not livro:
            messages.error(request, 'Não foi possível encontrar os detalhes deste livro.')
            return redirect('buscar_livro')

        context = {
            'livro': livro,
            'titulo_pagina': livro.get('titulo', 'Detalhes do Livro')
        }

        return render(request, 'detalhe_livro_google.html', context)  # Note o nome correto do template

    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do livro Google {livro_id}: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao buscar os detalhes do livro.')
        return redirect('buscar_livro')


# ==========================================
# Views de Páginas Legais
# ==========================================

def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')


def termos_uso(request):
    return render(request, 'termos_uso.html')


# ==========================================
# Views de Registro
# ==========================================

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
                logger.error(f"Erro no registro de usuário: {str(e)}")
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


# ==========================================
# Funções Auxiliares
# ==========================================

def _processar_resultados_google_books(resultados):
    CAPA_PADRAO = static('images/capa-indisponivel.svg')

    livros_processados = []
    for item in resultados:
        imagem = item.get('imagem')
        if not imagem or imagem.strip() == '':
            imagem = CAPA_PADRAO

        livro = {
            'id': item.get('id', ''),
            'titulo': item.get('titulo', 'Título não disponível'),
            'autor': item.get('autor', 'Autor não disponível'),
            'descricao': item.get('descricao', 'Descrição não disponível'),
            'imagem': imagem,
            'data_publicacao': item.get('data_publicacao', 'Data não disponível'),
            'editora': item.get('editora', 'Editora não disponível'),
            'paginas': item.get('numero_paginas', 'Não disponível'),
            'categorias': item.get('categoria', 'Não categorizado'),
            'idioma': item.get('idioma', 'Não especificado'),
            'link': item.get('link', '#'),
            'isbn': item.get('isbn', 'ISBN não disponível'),
        }
        livros_processados.append(livro)
    return livros_processados


def _ordenar_resultados(livros, ordem):
    if ordem == 'title':
        return sorted(livros, key=lambda x: x['titulo'])
    elif ordem == 'date':
        return sorted(livros, key=lambda x: x['data_publicacao'], reverse=True)
    return livros


def _paginar_resultados(livros, pagina):
    paginator = Paginator(livros, 9)
    try:
        return paginator.page(pagina)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def _enviar_email_contato(dados):
    corpo_email = f"""
    Nova mensagem de contato recebida:

    Nome: {dados['nome']}
    Email: {dados['email']}
    Assunto: {dados['assunto']}

    Mensagem:
    {dados['mensagem']}
    """

    send_mail(
        subject=f'Nova mensagem de {dados["nome"]}: {dados["assunto"]}',
        message=corpo_email,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[admin[1] for admin in settings.ADMINS],
        fail_silently=False,
    )