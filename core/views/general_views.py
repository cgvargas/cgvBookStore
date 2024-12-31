# core/views/general_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.urls import reverse

from core.presentation.forms.contact.contact_form import ContatoForm  # Nova importação
from core.forms import CustomUserCreationForm  # Mantido temporariamente
from core.utils.email_utils import enviar_email_contato, logger

# Importação dos repositories
from core.infrastructure.persistence.django.repositories.books.book_repository import BookRepository
from core.infrastructure.persistence.django.repositories.media.external_url_repository import ExternalURLRepository
from core.infrastructure.persistence.django.repositories.media.youtube_video_repository import YouTubeVideoRepository
from core.infrastructure.persistence.django.repositories.contact.contact_repository import ContactRepository

# Inicialização dos repositories
book_repository = BookRepository()
external_url_repository = ExternalURLRepository()
youtube_video_repository = YouTubeVideoRepository()
contact_repository = ContactRepository()

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('login')
                    })

                messages.success(
                    request,
                    'Conta criada com sucesso! Agora você pode fazer login.',
                    extra_tags='register success'
                )
                return redirect('login')

            except Exception as e:
                print(f"Erro ao registrar usuário: {e}")

                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Ocorreu um erro ao criar sua conta. Por favor, tente novamente.'
                    })

                messages.error(
                    request,
                    'Ocorreu um erro ao criar sua conta. Por favor, tente novamente.',
                    extra_tags='register error'
                )
    else:
        form = CustomUserCreationForm()

    return render(request, 'registro.html', {'form': form})

def index(request):
    try:
        # Obtendo os livros através dos repositories
        livros_destaque = book_repository.get_featured_books(
            order_by=['-data_publicacao', 'titulo'],
            limit=8
        )
        livros_mais_vendidos = book_repository.get_bestseller_books(
            order_by=['titulo'],
            limit=8
        )

        # Obtendo URLs externas e vídeos através dos repositories
        try:
            urls_externas = external_url_repository.get_all_urls()
        except Exception as e:
            logger.error(f"Erro ao buscar URLs externas: {str(e)}")
            urls_externas = []

        try:
            videos_youtube = youtube_video_repository.get_all_videos()
        except Exception as e:
            logger.error(f"Erro ao buscar vídeos do YouTube: {str(e)}")
            videos_youtube = []

        context = {
            'livros_destaque': livros_destaque,
            'livros_mais_vendidos': livros_mais_vendidos,
            'urls_externas': urls_externas,
            'videos_youtube': videos_youtube,
        }

        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Erro na view index: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao carregar a página inicial.')
        return render(request, 'index.html', {
            'livros_destaque': [],
            'livros_mais_vendidos': [],
            'urls_externas': [],
            'videos_youtube': [],
        })

def sobre(request):
    return render(request, 'sobre.html')


# core/views/general_views.py
def contato(request):
    logger.info("Método da requisição: %s", request.method)

    if request.method == 'POST':
        # Log dos dados brutos do POST
        logger.info("POST data: %s", dict(request.POST))

        form = ContatoForm(request.POST)
        logger.info("Form criado com dados do POST")

        # Log dos campos do formulário
        logger.info("Campos do formulário: %s", form.fields.keys())

        if form.is_valid():
            logger.info("Form é válido")
            try:
                dados_contato = {
                    'nome': form.cleaned_data['nome'],
                    'email': form.cleaned_data['email'],
                    'assunto': form.cleaned_data['assunto'],
                    'mensagem': form.cleaned_data['mensagem']
                }
                logger.info("Dados limpos: %s", dados_contato)

                # Salvar usando o repository
                contato = contact_repository.save_contact(dados_contato)
                logger.info("Contato salvo com sucesso: %s", contato)

                # Tentar enviar email
                emails_enviados = enviar_email_contato(dados_contato)
                logger.info("Status do envio de email: %s", emails_enviados)

                if emails_enviados:
                    messages.success(request, 'Mensagem enviada com sucesso!', extra_tags='contact success')
                else:
                    messages.warning(request, 'Mensagem recebida, mas houve um problema com o email.',
                                     extra_tags='contact warning')
                return redirect('contato')
            except Exception as e:
                logger.error("Erro ao processar contato: %s", str(e), exc_info=True)
                messages.error(request, 'Erro ao processar mensagem. Tente novamente.', extra_tags='contact error')
        else:
            logger.error("Erros de validação: %s", form.errors)
            for field, errors in form.errors.items():
                logger.error("Campo %s: %s", field, errors)
    else:
        form = ContatoForm()
        logger.info("Novo formulário criado")

    return render(request, 'contato.html', {'form': form})

def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')

def termos_uso(request):
    return render(request, 'termos_uso.html')