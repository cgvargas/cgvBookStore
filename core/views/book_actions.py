# core/views/book_actions.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.contrib import messages
from ..api import google_books_api
import logging
from django.urls import reverse

# Importação dos repositories
from core.infrastructure.persistence.django.repositories.books.bookshelf_repository import BookShelfRepository
from core.infrastructure.persistence.django.repositories.users.activity_history_repository import \
    ActivityHistoryRepository

logger = logging.getLogger(__name__)

# Inicialização dos repositories
book_shelf_repository = BookShelfRepository()
activity_history_repository = ActivityHistoryRepository()


@login_required
def adicionar_estante(request, livro_id):
    if request.method == 'POST':
        logger.info(f"Recebendo POST para adicionar livro {livro_id}")
        try:
            # Verifica se o livro já existe na estante
            if book_shelf_repository.book_exists_in_shelf(request.user, livro_id):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Este livro já está em sua estante!'
                    })
                messages.warning(request, 'Este livro já está em sua estante!')
                return redirect('google_book_detail', livro_id=livro_id)

            # Busca os detalhes do livro na API do Google
            livro_info = google_books_api.buscar_detalhes(livro_id)
            logger.debug(f"Dados recebidos da API: {livro_info}")

            tipo = request.POST.get('tipo', 'vou_ler')

            # Cria o livro na estante usando o repository
            estante_livro = book_shelf_repository.add_google_book_to_shelf(
                user=request.user,
                google_book_id=livro_id,
                book_type=tipo,
                book_data=livro_info
            )

            logger.info(f"Livro {livro_id} adicionado com sucesso à estante")  # Log atualizado

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Livro adicionado com sucesso à sua estante!',
                    'redirect_url': reverse('profile')
                })

            messages.success(request, 'Livro adicionado com sucesso à sua estante!')
            logger.info(f"Redirecionando para perfil após adicionar livro {livro_id}")  # Novo log
            return redirect('profile')

        except Exception as e:
            logger.error(f"Erro ao adicionar livro à estante: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Erro ao adicionar livro à estante.'
                })
            messages.error(request, 'Erro ao adicionar livro à estante.')
            return redirect('google_book_detail', livro_id=livro_id)

    return redirect('google_book_detail', livro_id=livro_id)


@login_required
def get_shelf_books(request, shelf_type):
    """Retorna os livros de uma determinada prateleira"""
    books = book_shelf_repository.get_user_books_by_type(
        user=request.user,
        book_type=shelf_type
    )

    html = render_to_string('partials/shelf_form.html', {
        'livros': books,
        'tipo': shelf_type
    })

    return JsonResponse({
        'html': html,
        'status': 'success'
    })


@login_required
@require_POST
def excluir_livro(request, livro_id):
    logger.info(f"Recebida requisição para excluir livro {livro_id}")

    # Verificar se é uma requisição AJAX
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        success = book_shelf_repository.delete_user_book(request.user, livro_id)

        if success:
            logger.info(f"Livro excluído com sucesso")

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': 'Livro excluído com sucesso',
                    'redirect_url': reverse('profile')
                })

            messages.success(request, 'Livro excluído com sucesso')
            return redirect('profile')

        else:
            logger.warning(f"Livro {livro_id} não encontrado")

            if is_ajax:
                return JsonResponse({
                    'success': False,
                    'message': 'Livro não encontrado',
                }, status=404)

            messages.error(request, 'Livro não encontrado')
            return redirect('profile')

    except Exception as e:
        logger.error(f"Erro ao excluir livro: {str(e)}")

        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': str(e),
            }, status=500)

        messages.error(request, f'Erro ao excluir o livro: {str(e)}')
        return redirect('profile')


@require_POST
@login_required
def transferir_livro(request, livro_id):
    novo_tipo = request.POST.get('novo_tipo')

    try:
        livro = book_shelf_repository.transfer_book(
            user=request.user,
            book_id=livro_id,
            new_type=novo_tipo
        )

        if livro:
            # Registra a atividade
            activity_history_repository.register_book_transfer(
                user=request.user,
                book_id=livro.livro_id,
                book_title=livro.titulo,
                old_type=livro.tipo,
                new_type=novo_tipo
            )

            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Tipo inválido'})

    except Exception as e:
        logger.error(f"Erro ao transferir livro: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)})