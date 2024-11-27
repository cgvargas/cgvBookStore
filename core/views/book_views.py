# book_views.py
import logging
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from ..models import Livro, EstanteLivro
from ..api import google_books_api
from .utils import _processar_resultados_google_books, _ordenar_resultados, _paginar_resultados

logger = logging.getLogger(__name__)

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
                messages.info(request, 'Nenhum livro encontrado...', extra_tags='busca')

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

        return render(request, 'detalhe_livro_google.html', context)

    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do livro Google {livro_id}: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao buscar os detalhes do livro.')
        return redirect('buscar_livro')

@login_required
def adicionar_estante(request, livro_id):
    if request.method == 'POST':
        try:
            livro = EstanteLivro.objects.create(
                usuario=request.user,
                livro_id=request.POST['livro_id'],
                tipo=request.POST['tipo'],
                titulo=request.POST['titulo'],
                autor=request.POST['autor'],
                capa=request.POST['capa'],
                data_lancamento=request.POST['data_lancamento'],
                sinopse=request.POST['sinopse']
            )
            logger.info(f"Livro criado com sucesso: {livro.id}")
            messages.success(request, 'Livro adicionado com sucesso!')
            return redirect('profile')
        except Exception as e:
            logger.error(f"Erro ao adicionar livro: {str(e)}")
            messages.error(request, 'Erro ao adicionar livro.')

    return redirect('google_book_detail', livro_id=livro_id)