from django.db import migrations
import logging

logger = logging.getLogger(__name__)


def populate_cache(apps, schema_editor):
    """
    Popula o NewLivroCache com dados da EstanteLivro
    """
    EstanteLivro = apps.get_model('core', 'EstanteLivro')
    NewLivroCache = apps.get_model('core', 'NewLivroCache')

    # Obtém livros únicos da estante
    livros_unicos = EstanteLivro.objects.values(
        'livro_id',  # Corrigido de book_id para livro_id
        'titulo',
        'autor',
        'categoria',
        'editora',
        'data_lancamento',  # Corrigido de data_publicacao
        'sinopse',  # Corrigido de descricao
        'isbn',
        'numero_paginas',
        'idioma',
        'capa'  # Corrigido de imagem_url
    ).distinct()

    # Prepara objetos para criação em massa
    cache_objects = []
    for livro in livros_unicos:
        try:
            cache_objects.append(
                NewLivroCache(
                    book_id=livro['livro_id'],  # Note que aqui mantemos book_id pois é o nome do campo no NewLivroCache
                    titulo=livro['titulo'],
                    autor=livro['autor'],
                    categoria=livro['categoria'],
                    editora=livro['editora'],
                    data_publicacao=livro['data_lancamento'],
                    descricao=livro['sinopse'],
                    isbn=livro['isbn'],
                    numero_paginas=livro['numero_paginas'],
                    idioma=livro['idioma'],
                    imagem_url=livro['capa']
                )
            )
        except Exception as e:
            logger.error(f"Erro ao processar livro {livro.get('titulo', 'Unknown')}: {str(e)}")

    # Cria registros em lotes para melhor performance
    if cache_objects:
        NewLivroCache.objects.bulk_create(
            cache_objects,
            batch_size=100,
            ignore_conflicts=True
        )
        logger.info(f"Migrados {len(cache_objects)} livros para o cache")
    else:
        logger.warning("Nenhum livro encontrado para migrar para o cache")


def reverse_populate(apps, schema_editor):
    """
    Reverte a população do cache limpando todos os registros
    """
    NewLivroCache = apps.get_model('core', 'NewLivroCache')
    NewLivroCache.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_remove_userpreferences_usuario_newlivrocache_and_more'),
    ]

    operations = [
        migrations.RunPython(populate_cache, reverse_populate),
    ]