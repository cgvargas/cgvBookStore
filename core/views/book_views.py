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
        ).exclude(id=livro.id)[:3]

        context = {
            'livro': livro,
            'livros_relacionados': livros_relacionados,
        }
        return render(request, 'livro_detail.html', context)
    except Exception as e:
        logger.error(f"Erro ao buscar detalhes do livro local {livro_id}: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao buscar os detalhes do livro.')
        return redirect('index')


@login_required
def buscar_livro(request):
    resultados = []
    mensagem = ''
    termo_busca = request.GET.get('query', '')
    tipo_busca = request.GET.get('tipo_busca', 'titulo')
    sem_resultados = False

    if termo_busca:
        try:
            # Busca no Google Books usando a API
            resultados = google_books_api.buscar_livros(
                termo_busca,
                tipo_busca=tipo_busca,
                max_results=40
            )

            if resultados:
                # Processa os resultados se necessário
                resultados = _processar_resultados_google_books(resultados)

                # Ordena os resultados se houver parâmetro de ordenação
                order_by = request.GET.get('order')
                if order_by:
                    resultados = _ordenar_resultados(resultados, order_by)

                # Paginação dos resultados
                page = request.GET.get('page')
                resultados = _paginar_resultados(resultados, page)
            else:
                logger.warning(f"Nenhum resultado encontrado para '{termo_busca}'")
                mensagem = f"Nenhum resultado encontrado para '{termo_busca}'. Deseja adicionar manualmente?"
                sem_resultados = True
                messages.info(request, mensagem, extra_tags='busca')

        except Exception as e:
            logger.error(f"Erro na busca: {str(e)}")
            mensagem = "Ocorreu um erro durante a busca. Tente novamente."
            messages.error(request, mensagem)

    context = {
        'livros': resultados,
        'query': termo_busca,
        'tipo_busca': tipo_busca,
        'mensagem': mensagem,
        'sem_resultados': sem_resultados
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