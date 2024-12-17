import re

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from core.infrastructure.persistence.django.models.recommendations import NewUserPreferences, NewLivroRecomendado
from core.models import EstanteLivro
from core.infrastructure.persistence.django.models import NewLivroCache
import logging


def normalizar_titulo(titulo):
    """Normaliza o título do livro para comparação"""
    if not titulo:
        return ""

    # Remove texto entre parênteses
    titulo = re.sub(r'\([^)]*\)', '', titulo)

    # Remove prefixos comuns de séries
    prefixos = [
        "crônicas de", "chronicles of", "saga", "série", "series",
        "vol.", "volume", "livro", "book", "parte", "part",
        "trilogia", "trilogy"
    ]

    titulo_lower = titulo.lower()
    for prefixo in prefixos:
        if titulo_lower.startswith(prefixo):
            titulo_lower = titulo_lower.replace(prefixo, "", 1)

    # Remove números e caracteres especiais
    titulo_clean = re.sub(r'[0-9#@$%^&*()_+\-=\[\]{};:"|<>?,.\/\\]', '', titulo_lower)

    # Remove palavras conectoras comuns
    conectores = ["de", "do", "da", "dos", "das", "the", "a", "an", "of"]
    palavras = titulo_clean.split()
    palavras = [p for p in palavras if p not in conectores]

    # Remove espaços extras e traços
    titulo_final = " ".join(palavras).strip().strip("-— ")

    return titulo_final


def normalizar_autor(autor):
    """Normaliza o nome do autor para comparação"""
    if not autor:
        return ""

    # Remove prefixos comuns
    prefixos = ["por", "by", "de"]
    autor_lower = autor.lower()
    for prefixo in prefixos:
        if autor_lower.startswith(prefixo):
            autor_lower = autor_lower.replace(prefixo, "", 1)

    # Separa os autores se houver múltiplos
    autores = re.split(r'[,&]', autor_lower)

    # Normaliza cada nome de autor
    autores_normalizados = []
    for nome in autores:
        # Remove espaços e caracteres especiais
        nome = re.sub(r'[^a-zA-Z\s]', '', nome)
        # Divide em palavras e ordena
        palavras = sorted(nome.split())
        # Junta novamente
        autores_normalizados.append(" ".join(palavras).strip())

    # Ordena os autores para garantir mesma ordem
    return ", ".join(sorted(autores_normalizados))


def titulos_similares(titulo1, titulo2):
    """Verifica se dois títulos são similares"""
    t1 = normalizar_titulo(titulo1)
    t2 = normalizar_titulo(titulo2)

    # Verifica se um título está contido no outro
    return t1 in t2 or t2 in t1


def autores_similares(autor1, autor2):
    """Verifica se dois conjuntos de autores são similares"""
    a1 = normalizar_autor(autor1)
    a2 = normalizar_autor(autor2)

    return a1 == a2

logger = logging.getLogger(__name__)


@login_required
def gerar_recomendacoes(request):
    """Gera recomendações para o usuário"""
    try:
        logger.info("Iniciando geração de recomendações...")

        # Verifica se o usuário tem livros na estante
        livros_estante = EstanteLivro.objects.filter(usuario=request.user)
        if not livros_estante.exists():
            logger.info("Usuário não possui livros na estante")
            return []

        # Obtém preferências
        preferences, created = NewUserPreferences.objects.get_or_create(usuario=request.user)
        preferences.atualizar_preferencias()

        logger.info(f"Preferências do usuário - Categorias: {preferences.categorias_favoritas}")
        logger.info(f"Preferências do usuário - Autores: {preferences.autores_favoritos}")

        # Obtém IDs dos livros do usuário (incluindo livros_id nulos)
        livros_usuario_ids = set(
            livros_estante.exclude(livro_id='')
            .exclude(livro_id__isnull=True)
            .values_list('livro_id', flat=True)
        )

        # Obtém informações de título e autor dos livros do usuário
        livros_usuario_info = list(livros_estante.values_list('titulo', 'autor'))

        logger.info(f"IDs de livros do usuário: {livros_usuario_ids}")

        # Busca livros no cache
        query = NewLivroCache.objects.all()
        if livros_usuario_ids:
            query = query.exclude(book_id__in=livros_usuario_ids)

        livros_cache = list(query.order_by('?')[:200])
        total_livros = len(livros_cache)

        logger.info(f"Encontrados {total_livros} livros no cache para análise")

        if total_livros == 0:
            logger.warning("Nenhum livro encontrado no cache para recomendações")
            return []

        # Calcula scores e armazena recomendações
        recomendacoes = []
        for livro_cache in livros_cache:
            if not livro_cache.titulo or not livro_cache.autor:
                logger.warning(f"Livro sem título ou autor encontrado no cache: {livro_cache.book_id}")
                continue

            # Verifica se já existe um livro similar
            livro_duplicado = False
            for titulo_estante, autor_estante in livros_usuario_info:
                if (titulos_similares(livro_cache.titulo, titulo_estante) and
                        autores_similares(livro_cache.autor, autor_estante)):
                    logger.info(
                        f"Livro similar '{livro_cache.titulo}' de {livro_cache.autor} já existe na estante do usuário")
                    livro_duplicado = True
                    break

            if livro_duplicado:
                continue

            score = preferences.calcular_score_livro(livro_cache)
            logger.info(f"Score calculado para '{livro_cache.titulo}': {score}")

            if score >= 1:
                recomendacao = NewLivroRecomendado(
                    usuario=request.user,
                    livro_id=livro_cache.book_id,
                    titulo=livro_cache.titulo,
                    autor=livro_cache.autor,
                    categoria=livro_cache.categoria or '',
                    score=score
                )
                recomendacoes.append(recomendacao)

        # Ordena por score e seleciona os top 8
        recomendacoes.sort(key=lambda x: x.score, reverse=True)
        top_recomendacoes = recomendacoes[:8]

        # Salva as recomendações
        NewLivroRecomendado.objects.filter(usuario=request.user).delete()
        if top_recomendacoes:
            NewLivroRecomendado.objects.bulk_create(top_recomendacoes)
            logger.info(f"Salvas {len(top_recomendacoes)} recomendações")
        else:
            logger.warning("Nenhuma recomendação gerada após análise")

        return top_recomendacoes

    except Exception as e:
        logger.error(f"Erro ao gerar recomendações: {str(e)}")
        return []


@login_required
def obter_recomendacoes_ajax(request):
    """Endpoint para obter recomendações via AJAX"""
    try:
        # Obtém as recomendações
        recomendacoes = gerar_recomendacoes(request)

        # Lista para armazenar as recomendações formatadas
        recomendacoes_formatadas = []

        for rec in recomendacoes:
            try:
                # Busca informações do livro no cache
                livro_cache = NewLivroCache.objects.get(book_id=rec.livro_id)

                # Obtém as preferências do usuário
                preferences = NewUserPreferences.objects.get(usuario=request.user)

                # Monta o dicionário de recomendação
                recomendacao = {
                    'id': rec.livro_id,
                    'titulo': rec.titulo,
                    'autor': rec.autor,
                    'categoria': rec.categoria,
                    'score': float(rec.score),
                    'capa': livro_cache.imagem_url,
                    'categoria_match': False,
                    'autor_match': False
                }

                # Verifica matches
                if rec.categoria and preferences.categorias_favoritas:
                    categoria_livro = rec.categoria.lower()
                    recomendacao['categoria_match'] = any(
                        cat.lower() in categoria_livro or
                        categoria_livro in cat.lower()
                        for cat in preferences.categorias_favoritas.keys()
                    )

                if rec.autor and preferences.autores_favoritos:
                    autor_livro = rec.autor.lower()
                    recomendacao['autor_match'] = any(
                        autor.lower() in autor_livro or
                        autor_livro in autor.lower()
                        for autor in preferences.autores_favoritos.keys()
                    )

                recomendacoes_formatadas.append(recomendacao)

            except NewLivroCache.DoesNotExist:
                logger.warning(f"Livro {rec.livro_id} não encontrado no cache")
                continue
            except Exception as e:
                logger.error(f"Erro ao processar recomendação: {str(e)}")
                continue

        return JsonResponse({
            'status': 'success',
            'recomendacoes': recomendacoes_formatadas
        })

    except Exception as e:
        logger.error(f"Erro nas recomendações: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def atualizar_preferencias(request):
    """Endpoint para atualizar preferências do usuário"""
    try:
        preferences, _ = NewUserPreferences.objects.get_or_create(usuario=request.user)
        preferences.atualizar_preferencias()
        logger.info("Preferências atualizadas com sucesso")

        return JsonResponse({
            'status': 'success',
            'message': 'Preferências atualizadas com sucesso'
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@login_required
def debug_recomendacoes(request):
    """Endpoint para debug do sistema de recomendações"""
    try:
        total_cache = NewLivroCache.objects.count()
        livros_usuario = EstanteLivro.objects.filter(usuario=request.user).count()
        preferences = NewUserPreferences.objects.get(usuario=request.user)

        return JsonResponse({
            'total_livros_cache': total_cache,
            'livros_usuario': livros_usuario,
            'categorias_favoritas': preferences.categorias_favoritas,
            'autores_favoritos': preferences.autores_favoritos
        })
    except Exception as e:
        return JsonResponse({'error': str(e)})