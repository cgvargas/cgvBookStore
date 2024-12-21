# core/views/general_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.urls import reverse

from core.forms import ContatoForm, CustomUserCreationForm
from core.utils.email_utils import enviar_email_contato

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
            order_by=['-data_publicacao', 'titulo']
        )
        livros_mais_vendidos = book_repository.get_bestseller_books(
            order_by=['titulo']
        )

        # Configuração da paginação
        paginator_destaque = Paginator(livros_destaque, 8)
        paginator_vendidos = Paginator(livros_mais_vendidos, 8)

        # Pegando a página da query string
        page_destaque = request.GET.get('page_destaque', 1)
        page_vendidos = request.GET.get('page_vendidos', 1)

        # Paginação para livros em destaque
        try:
            livros_destaque_paginated = paginator_destaque.page(page_destaque)
        except PageNotAnInteger:
            livros_destaque_paginated = paginator_destaque.page(1)
        except EmptyPage:
            livros_destaque_paginated = paginator_destaque.page(paginator_destaque.num_pages)

        # Paginação para livros mais vendidos
        try:
            livros_mais_vendidos_paginated = paginator_vendidos.page(page_vendidos)
        except PageNotAnInteger:
            livros_mais_vendidos_paginated = paginator_vendidos.page(1)
        except EmptyPage:
            livros_mais_vendidos_paginated = paginator_vendidos.page(paginator_vendidos.num_pages)

        # Obtendo URLs externas e vídeos através dos repositories
        urls_externas = external_url_repository.get_all_urls()
        videos_youtube = youtube_video_repository.get_all_videos()

        context = {
            'livros_destaque': livros_destaque_paginated,
            'livros_mais_vendidos': livros_mais_vendidos_paginated,
            'urls_externas': urls_externas,
            'videos_youtube': videos_youtube,
        }

        return render(request, 'index.html', context)
    except Exception as e:
        messages.error(request, 'Ocorreu um erro ao carregar a página inicial.')
        return render(request, 'index.html', {})

def sobre(request):
    return render(request, 'sobre.html')

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                contato = contact_repository.save_contact(form.cleaned_data)
                emails_enviados = enviar_email_contato(form.cleaned_data)

                if emails_enviados:
                    messages.success(
                        request,
                        'Mensagem enviada com sucesso! Verifique seu e-mail para confirmação.',
                        extra_tags='contact success'
                    )
                else:
                    messages.warning(
                        request,
                        'Sua mensagem foi recebida, mas houve um problema ao enviar o e-mail de confirmação.',
                        extra_tags='contact warning'
                    )

                return redirect('contato')
            except Exception as e:
                messages.error(
                    request,
                    'Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.',
                    extra_tags='contact error'
                )
    else:
        form = ContatoForm()

    return render(request, 'contato.html', {'form': form})

def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')

def termos_uso(request):
    return render(request, 'termos_uso.html')