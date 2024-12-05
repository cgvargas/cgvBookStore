# views/book_actions.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.contrib import messages
from ..models import EstanteLivro, HistoricoAtividade
from ..api import google_books_api
import logging

logger = logging.getLogger(__name__)


@login_required
def adicionar_estante(request, livro_id):
    if request.method == 'POST':
        logger.info(f"Recebendo POST para adicionar livro {livro_id}")
        logger.info(f"POST data: {request.POST}")
        try:
            # Verifica se o livro já existe na estante do usuário
            if EstanteLivro.objects.filter(usuario=request.user, livro_id=livro_id).exists():
                messages.warning(request, 'Este livro já está em sua estante!')
                return redirect('google_book_detail', livro_id=livro_id)

            # Busca os detalhes do livro na API do Google
            livro_info = google_books_api.buscar_detalhes(livro_id)

            # Tipo deve vir do formulário ou request.POST
            tipo = request.POST.get('tipo', 'vou_ler')  # default para 'vou_ler' se não especificado

            # Cria o livro na estante
            estante_livro = EstanteLivro.objects.create(
                usuario=request.user,
                livro_id=livro_id,
                tipo=tipo,  # usa o tipo especificado
                titulo=livro_info.get('titulo', ''),
                autor=livro_info.get('autor', ''),
                capa=livro_info.get('imagem', ''),
                data_lancamento=livro_info.get('data_publicacao', ''),
                sinopse=livro_info.get('descricao', '')
            )

            # Registra a atividade
            HistoricoAtividade.objects.create(
                usuario=request.user,
                acao='adicao',
                livro_id=livro_id,
                titulo_livro=estante_livro.titulo,
                detalhes=f"Livro adicionado à estante '{tipo}'"
            )

            messages.success(request, 'Livro adicionado com sucesso à sua estante!')
            return redirect('profile')

        except Exception as e:
            logger.error(f"Erro ao adicionar livro à estante: {str(e)}")
            messages.error(request, 'Erro ao adicionar livro à estante.')
            return redirect('google_book_detail', livro_id=livro_id)

    return redirect('google_book_detail', livro_id=livro_id)


@login_required
def get_shelf_books(request, shelf_type):
    """Retorna os livros de uma determinada prateleira"""
    books = EstanteLivro.objects.filter(
        usuario=request.user,
        tipo=shelf_type
    ).order_by('titulo')

    html = render_to_string('partials/shelf_form.html', {
        'livros': books,
        'tipo': shelf_type
    })

    return JsonResponse({
        'html': html,
        'status': 'success'
    })


@require_POST
@login_required
def excluir_livro(request, livro_id):
    livro = get_object_or_404(EstanteLivro, id=livro_id, usuario=request.user)
    tipo_anterior = livro.tipo
    livro.delete()

    HistoricoAtividade.objects.create(
        usuario=request.user,
        acao='exclusao',
        livro_id=livro.livro_id,
        titulo_livro=livro.titulo,
        detalhes=f"Livro removido da estante {tipo_anterior}"
    )

    return JsonResponse({'status': 'success'})


@require_POST
@login_required
def transferir_livro(request, livro_id):
    livro = get_object_or_404(EstanteLivro, id=livro_id, usuario=request.user)
    novo_tipo = request.POST.get('novo_tipo')

    if novo_tipo in dict(EstanteLivro.TIPO_CHOICES):
        tipo_anterior = livro.tipo
        livro.tipo = novo_tipo
        livro.save()

        HistoricoAtividade.objects.create(
            usuario=request.user,
            acao='transferencia',
            livro_id=livro.livro_id,
            titulo_livro=livro.titulo,
            detalhes=f"Livro transferido de {tipo_anterior} para {novo_tipo}"
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Tipo inválido'})