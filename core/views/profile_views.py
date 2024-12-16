# profile_views.py
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
from core.models import EstanteLivro, LivroCache
from .recommendation_views import gerar_recomendacoes
from analytics.utils import register_book_view

ITEMS_PER_PAGE = 8
logger = logging.getLogger(__name__)

User = get_user_model()

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

        # Busca recomendações e formata com informações completas
        recomendacoes_raw = gerar_recomendacoes(request)
        recomendacoes = []

        for rec in recomendacoes_raw:
            try:
                livro_cache = LivroCache.objects.get(book_id=rec.livro_id)
                recomendacoes.append({
                    'id': rec.livro_id,  # Mantemos o ID do Google Books
                    'titulo': rec.titulo,
                    'autor': rec.autor,
                    'categoria': rec.categoria,
                    'score': float(rec.score),
                    'capa': livro_cache.imagem_url
                })
            except LivroCache.DoesNotExist:
                logger.warning(f"Livro {rec.livro_id} não encontrado no cache")
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
            livro = form.save(commit=False)
            livro.usuario = request.user
            livro.manual = True
            livro.save()

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
            # Formata os erros de uma maneira mais amigável
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]

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
    """Edita um livro existente na estante"""
    livro = get_object_or_404(EstanteLivro, id=livro_id, usuario=request.user)
    form = LivroManualForm(instance=livro)  # Inicializa o form aqui

    if request.method == 'POST':
        try:
            form = LivroManualForm(request.POST, instance=livro)  # Redefine o form com os dados POST
            if form.is_valid():
                livro_atualizado = form.save(commit=False)
                livro_atualizado.usuario = request.user
                livro_atualizado.save()
                messages.add_message(request, messages.INFO, 'Livro atualizado com sucesso!')
                return redirect('detalhes_livro', livro_id=livro.id)
            else:
                messages.add_message(request, messages.ERROR, 'Por favor, corrija os erros no formulário.')
        except Exception as e:
            messages.add_message(request, messages.ERROR, f'Erro ao atualizar o livro. Tente novamente. {str(e)}')
            logger.error(f"Erro ao atualizar livro: {str(e)}")

    return render(request, 'editar_livro.html', {
        'form': form,
        'livro': livro
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
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


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
@require_http_methods(["POST"])
def update_profile(request):
    try:
        user = request.user
        print("Dados recebidos:", request.POST)  # Debug

        nome_completo = request.POST.get('nome_completo')
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Atualiza os dados
        user.nome_completo = nome_completo
        user.username = username
        user.email = email
        user.save()

        return JsonResponse({
            'status': 'success',
            'user': {
                'nome_completo': user.nome_completo,
                'username': user.username,
                'email': user.email
            }
        })
    except Exception as e:
        print("Erro ao atualizar perfil:", str(e))  # Debug
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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


# Detalhe para os livros das prateleiras
def detalhes_livro(request, livro_id):
    livro = get_object_or_404(EstanteLivro, id=livro_id)

    # Registra visualização no analytics
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
            'preco': livro.preco if hasattr(livro, 'preco') else None,
            'moeda': 'BRL',  # ou adicione um campo no seu modelo para isso
            'classificacao': livro.classificacao # Adicionando o campo de classificação
        }
    }
    print(f"Classificação atual do livro: {livro.classificacao}")
    return render(request, 'detalhes_livros.html', context)


@csrf_exempt  # Temporário para teste
@require_POST
def salvar_classificacao(request, livro_id):
    try:
        livro = EstanteLivro.objects.get(id=livro_id)  # Mudando de Livro para EstanteLivro
        classificacao = int(request.POST.get('classificacao'))

        if 1 <= classificacao <= 5:
            livro.classificacao = classificacao
            livro.save()
            print(f"Classificação {classificacao} salva para o livro {livro.id}")  # Debug
            return JsonResponse({
                'success': True,
                'message': 'Classificação salva com sucesso!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'A classificação deve ser entre 1 e 5'
            }, status=400)

    except EstanteLivro.DoesNotExist:  # Mudando a exceção também
        return JsonResponse({
            'success': False,
            'message': 'Livro não encontrado'
        }, status=404)
    except Exception as e:
        print(f"Erro ao salvar classificação: {str(e)}")  # Debug
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)