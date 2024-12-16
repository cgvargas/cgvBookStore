# general_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import Livro, URLExterna, VideoYouTube
from ..forms import ContatoForm, CustomUserCreationForm
from ..utils.email_utils import enviar_email_contato
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.urls import reverse


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()

                # Se a requisição for AJAX, retorna JSON
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('login')
                    })

                # Se for uma requisição normal, adiciona mensagem e redireciona
                messages.success(
                    request,
                    'Conta criada com sucesso! Agora você pode fazer login.',
                    extra_tags='register success'
                )
                return redirect('login')

            except Exception as e:
                # Log do erro (opcional)
                print(f"Erro ao registrar usuário: {e}")

                # Se for AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'Ocorreu um erro ao criar sua conta. Por favor, tente novamente.'
                    })

                # Se for requisição normal
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
        # Obtendo os livros para destaque e mais vendidos
        livros_destaque = Livro.objects.filter(destaque=True).order_by('-data_publicacao', 'titulo')
        livros_mais_vendidos = Livro.objects.filter(mais_vendido=True).order_by('titulo')

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

        # Contexto da view
        context = {
            'livros_destaque': livros_destaque_paginated,
            'livros_mais_vendidos': livros_mais_vendidos_paginated,
            'urls_externas': URLExterna.objects.all(),
            'videos_youtube': VideoYouTube.objects.all(),
        }

        return render(request, 'index.html', context)
    except Exception as e:
        # Mensagem de erro
        messages.error(request, 'Ocorreu um erro ao carregar a página inicial.')
        return render(request, 'index.html', {})

def sobre(request):
    return render(request, 'sobre.html')

def contato(request):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            try:
                contato = form.save()
                emails_enviados = enviar_email_contato(form.cleaned_data)

                print("Form salvo:", contato)  # Debug
                print("Emails enviados:", emails_enviados)  # Debug

                if emails_enviados:
                    messages.success(
                        request,
                        'Mensagem enviada com sucesso! Verifique seu e-mail para confirmação.',
                        extra_tags='contact success'  # Adicionando ambas as tags

                    )
                    print("Mensagem de sucesso adicionada")  # Debug
                else:
                    messages.warning(
                        request,
                        'Sua mensagem foi recebida, mas houve um problema ao enviar o e-mail de confirmação.',
                        extra_tags='contact warning'
                    )
                    print("Mensagem de aviso adicionada")  # Debug

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