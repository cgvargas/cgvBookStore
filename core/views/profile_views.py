# profile_views.py
import logging
import os
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count
from django.contrib import messages
from django.views.decorators.http import require_http_methods

from core.models import EstanteLivro
from core.forms import LivroManualForm  # Importando o novo form que criamos

ITEMS_PER_PAGE = 8
logger = logging.getLogger(__name__)


def get_paginated_books(queryset, page_number):
    """Helper function to handle pagination"""
    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    try:
        return paginator.page(page_number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


@login_required
def profile(request):
    # Buscar livros com anotações em uma única query
    estantes = {
        'favorito': request.GET.get('page_fav'),
        'lendo': request.GET.get('page_lendo'),
        'vou_ler': request.GET.get('page_vou_ler'),
        'lido': request.GET.get('page_lidos')
    }

    # Otimizar queries usando select_related se houver relações
    livros_paginados = {}
    for tipo, page in estantes.items():
        queryset = EstanteLivro.objects.filter(
            usuario=request.user,
            tipo=tipo
        ).order_by('-data_adicao')
        livros_paginados[tipo] = get_paginated_books(queryset, page)

    # Fazer contagem apenas de livros válidos
    total_livros = EstanteLivro.objects.filter(
        usuario=request.user,
        titulo__isnull=False
    ).distinct().count()

    context = {
        'favoritos': livros_paginados['favorito'],
        'lendo': livros_paginados['lendo'],
        'vou_ler': livros_paginados['vou_ler'],
        'lidos': livros_paginados['lido'],
        'total_livros': total_livros
    }

    return render(request, 'perfil.html', context)


@login_required
@require_http_methods(["POST"])
def adicionar_livro_manual(request):
    form = LivroManualForm(request.POST)
    if form.is_valid():
        livro = form.save(commit=False)
        livro.usuario = request.user
        livro.save()

        return JsonResponse({
            'success': True,
            'message': 'Livro adicionado com sucesso!',
            'livro': {
                'id': livro.id,
                'titulo': livro.titulo,
                'autor': livro.autor,
                'capa': livro.capa
            }
        })
    else:
        return JsonResponse({
            'success': False,
            'error': form.errors
        })



@login_required
def editar_livro_manual(request, livro_id):
    """Edita um livro existente na estante"""
    livro = get_object_or_404(EstanteLivro, id=livro_id, usuario=request.user)

    if request.method == 'POST':
        try:
            form = LivroManualForm(request.POST, instance=livro)
            if form.is_valid():
                livro = form.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Livro atualizado com sucesso!',
                    'livro': {
                        'id': livro.id,
                        'titulo': livro.titulo,
                        'autor': livro.autor,
                        'capa': livro.capa,
                        'descricao': livro.sinopse,
                        'editora': livro.editora,
                        'data_publicacao': livro.data_lancamento,
                        'numero_paginas': livro.numero_paginas,
                        'idioma': livro.idioma,
                        'categoria': livro.categoria,
                        'isbn': livro.isbn,
                        'notas_pessoais': livro.notas_pessoais,
                        'tipo': livro.tipo
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Dados inválidos',
                    'errors': form.errors
                })

        except Exception as e:
            logger.error(f"Erro ao atualizar livro: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Erro ao atualizar o livro. Tente novamente.'
            })

    # Para requisições GET, retornamos o formulário inicial com os dados do livro
    form = LivroManualForm(instance=livro)
    return JsonResponse({
        'success': True,
        'livro': {
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'capa': livro.capa,
            'descricao': livro.sinopse,
            'editora': livro.editora,
            'data_publicacao': livro.data_lancamento,
            'numero_paginas': livro.numero_paginas,
            'idioma': livro.idioma,
            'categoria': livro.categoria,
            'isbn': livro.isbn,
            'notas_pessoais': livro.notas_pessoais,
            'tipo': livro.tipo
        }
    })

@login_required
@require_http_methods(["POST"])
def excluir_livro(request, livro_id):
    """Exclui um livro da estante"""
    try:
        livro = get_object_or_404(EstanteLivro, id=livro_id, usuario=request.user)
        livro.delete()

        return JsonResponse({
            'success': True,
            'message': 'Livro removido com sucesso!'
        })

    except Exception as e:
        logger.error(f"Erro ao excluir livro: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Erro ao remover o livro. Tente novamente.'
        })


# Manter suas funções existentes de atualização de foto de perfil
@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        try:
            # Deletar foto antiga se existir
            if request.user.profile_image:
                request.user.profile_image.delete()

            # Salvar nova foto
            request.user.profile_image = request.FILES['profile_photo']
            request.user.save()

            return JsonResponse({
                'success': True,
                'message': 'Foto atualizada com sucesso!',
                'image_url': request.user.profile_image.url
            })
        except Exception as e:
            logger.error(f"Erro ao atualizar foto: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Erro ao atualizar a foto.'
            })

    return JsonResponse({
        'success': False,
        'error': 'Requisição inválida.'
    })


@login_required
def delete_profile_photo(request):
    if request.method == 'POST':
        try:
            if request.user.profile_image:
                request.user.profile_image.delete()
                request.user.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Foto removida com sucesso!'
                })
        except Exception as e:
            logger.error(f"Erro ao remover foto: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Erro ao remover a foto.'
            })

    return JsonResponse({
        'success': False,
        'error': 'Requisição inválida.'
    })


@login_required
def verificar_livro_existente(request):
    """
    Verifica se um livro já existe na estante do usuário
    """
    titulo = request.GET.get('titulo', '').strip()
    autor = request.GET.get('autor', '').strip()

    if not titulo or not autor:
        return JsonResponse({
            'exists': False,
            'error': 'Título e autor são necessários para a verificação.'
        })

    # Faz a verificação de forma case-insensitive
    livro_existe = EstanteLivro.objects.filter(
        usuario=request.user,
        titulo__iexact=titulo,
        autor__iexact=autor
    ).exists()

    # Se o livro existir, busca detalhes adicionais
    if livro_existe:
        livro = EstanteLivro.objects.filter(
            usuario=request.user,
            titulo__iexact=titulo,
            autor__iexact=autor
        ).first()

        return JsonResponse({
            'exists': True,
            'message': 'Livro já existe na sua estante.',
            'detalhes': {
                'id': livro.id,
                'tipo': livro.tipo,
                'tipo_display': livro.get_tipo_display(),
                'data_adicao': livro.data_adicao.strftime('%d/%m/%Y')
            }
        })

    return JsonResponse({
        'exists': False,
        'message': 'Livro não encontrado na sua estante.'
    })