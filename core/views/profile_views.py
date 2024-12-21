# core/views/profile_views.py
from django.contrib import messages
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt

from core.forms import LivroManualForm
from analytics.utils import register_book_view

# Importação dos repositories
from core.infrastructure.persistence.django.repositories.books.book_repository import BookRepository
from core.infrastructure.persistence.django.repositories.books.book_cache_repository import BookCacheRepository
from core.infrastructure.persistence.django.repositories.books.bookshelf_repository import BookShelfRepository
from core.infrastructure.persistence.django.repositories.recommendation_repository import DjangoRecommendationRepository

ITEMS_PER_PAGE = 8
logger = logging.getLogger(__name__)
User = get_user_model()

# Inicialização dos repositories
book_repository = BookRepository()
book_cache_repository = BookCacheRepository()
book_shelf_repository = BookShelfRepository()
recommendation_repository = DjangoRecommendationRepository()

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
    try:
        # Buscar livros com anotações em uma única query
        estantes = {
            'favorito': request.GET.get('page_fav'),
            'lendo': request.GET.get('page_lendo'),
            'vou_ler': request.GET.get('page_vou_ler'),
            'lido': request.GET.get('page_lidos')
        }

        # Otimizar queries com repositories
        livros_paginados = {}
        for tipo, page in estantes.items():
            queryset = book_shelf_repository.get_user_books_by_type(request.user, tipo)
            livros_paginados[tipo] = get_paginated_books(queryset, page)

        total_livros = book_shelf_repository.count_valid_user_books(request.user)

        # Busca recomendações através do repository
        recomendacoes_raw = recommendation_repository.get_user_recommendations(request.user.id)
        recomendacoes = []

        for rec in recomendacoes_raw:
            try:
                livro_cache = book_cache_repository.get_book_by_id(rec.livro_id)
                recomendacoes.append({
                    'id': rec.livro_id,
                    'titulo': rec.titulo,
                    'autor': rec.autor,
                    'categoria': rec.categoria,
                    'score': float(rec.score),
                    'capa': livro_cache.imagem_url if livro_cache else None
                })
            except Exception as e:
                logger.warning(f"Livro {rec.livro_id} não encontrado no cache: {str(e)}")
                continue

        context = {
            'favoritos': livros_paginados['favorito'],
            'lendo': livros_paginados['lendo'],
            'vou_ler': livros_paginados['vou_ler'],
            'lidos': livros_paginados['lido'],
            'total_livros': total_livros,
            'recomendacoes': recomendacoes,
        }

        return render(request, 'perfil.html', context)

    except Exception as e:
        logger.error(f"Erro na view profile: {str(e)}")
        messages.error(request, "Ocorreu um erro ao carregar o perfil.")
        return redirect('index')

@login_required
@require_http_methods(["POST"])
def adicionar_livro_manual(request):
    try:
        form = LivroManualForm(request.POST)
        if form.is_valid():
            livro = book_shelf_repository.create_manual_book(
                user=request.user,
                book_data=form.cleaned_data
            )

            return JsonResponse({
                'success': True,
                'message': 'Livro adicionado com sucesso!',
                'livro': {
                    'id': livro.id,
                    'titulo': livro.titulo,
                    'autor': livro.autor,
                    'capa': livro.capa,
                    'tipo': livro.tipo
                }
            })
        else:
            errors = {field: [str(error) for error in error_list]
                     for field, error_list in form.errors.items()}
            return JsonResponse({
                'success': False,
                'error': errors
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def editar_livro_manual(request, livro_id):
    livro = book_shelf_repository.get_user_book_by_id(request.user, livro_id)
    if not livro:
        messages.error(request, "Livro não encontrado.")
        return redirect('profile')

    if request.method == 'POST':
        try:
            form = LivroManualForm(request.POST, instance=livro)
            if form.is_valid():
                livro_atualizado = book_shelf_repository.update_manual_book(
                    user=request.user,
                    book_id=livro_id,
                    book_data=form.cleaned_data
                )
                messages.success(request, 'Livro atualizado com sucesso!')
                return redirect('detalhes_livro', livro_id=livro_atualizado.id)
            else:
                messages.error(request, 'Por favor, corrija os erros no formulário.')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar o livro: {str(e)}')
            logger.error(f"Erro ao atualizar livro: {str(e)}")

    form = LivroManualForm(instance=livro)
    return render(request, 'editar_livro.html', {
        'form': form,
        'livro': livro
    })

@login_required
@require_http_methods(["POST"])
def excluir_livro(request, livro_id):
    try:
        success = book_shelf_repository.delete_user_book(request.user, livro_id)
        if success:
            return JsonResponse({
                'success': True,
                'message': 'Livro removido com sucesso!'
            })
        return JsonResponse({
            'success': False,
            'error': 'Livro não encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def update_profile_photo(request):
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        try:
            updated_user = book_repository.update_user_profile_photo(
                user=request.user,
                photo=request.FILES['profile_photo']
            )
            return JsonResponse({
                'success': True,
                'message': 'Foto atualizada com sucesso!',
                'image_url': updated_user.profile_image.url
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
            success = book_repository.delete_user_profile_photo(request.user)
            if success:
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
@require_http_methods(["POST"])
def update_profile(request):
    try:
        updated_user = book_repository.update_user_profile(
            user=request.user,
            profile_data={
                'nome_completo': request.POST.get('nome_completo'),
                'username': request.POST.get('username'),
                'email': request.POST.get('email')
            }
        )
        return JsonResponse({
            'status': 'success',
            'user': {
                'nome_completo': updated_user.nome_completo,
                'username': updated_user.username,
                'email': updated_user.email
            }
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar perfil: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
def verificar_livro_existente(request):
    titulo = request.GET.get('titulo', '').strip()
    autor = request.GET.get('autor', '').strip()

    if not titulo or not autor:
        return JsonResponse({
            'exists': False,
            'error': 'Título e autor são necessários para a verificação.'
        })

    livro = book_shelf_repository.get_user_book_by_title_author(
        user=request.user,
        titulo=titulo,
        autor=autor
    )

    if livro:
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

@login_required
def detalhes_livro(request, livro_id):
    livro = book_shelf_repository.get_user_book_by_id(request.user, livro_id)
    if not livro:
        messages.error(request, "Livro não encontrado.")
        return redirect('profile')

    try:
        register_book_view(livro.titulo, request.user)
    except Exception as e:
        logger.warning(f"Erro ao registrar visualização do livro {livro_id}: {str(e)}")

    context = {
        'livro': {
            'id': livro.id,
            'titulo': livro.titulo,
            'autor': livro.autor,
            'imagem': livro.capa,
            'descricao': livro.sinopse,
            'editora': livro.editora,
            'data_publicacao': livro.data_lancamento,
            'numero_paginas': livro.numero_paginas,
            'isbn': livro.isbn,
            'idioma': livro.idioma,
            'categoria': livro.categoria,
            'preco': getattr(livro, 'preco', None),
            'moeda': 'BRL',
            'classificacao': livro.classificacao
        }
    }
    return render(request, 'detalhes_livros.html', context)

@csrf_exempt
@require_POST
def salvar_classificacao(request, livro_id):
    try:
        classificacao = int(request.POST.get('classificacao'))
        if not 1 <= classificacao <= 5:
            return JsonResponse({
                'success': False,
                'message': 'A classificação deve ser entre 1 e 5'
            }, status=400)

        success = book_shelf_repository.update_book_rating(
            user=request.user,
            book_id=livro_id,
            rating=classificacao
        )

        if success:
            return JsonResponse({
                'success': True,
                'message': 'Classificação salva com sucesso!'
            })
        return JsonResponse({
            'success': False,
            'message': 'Livro não encontrado'
        }, status=404)

    except Exception as e:
        logger.error(f"Erro ao salvar classificação: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)