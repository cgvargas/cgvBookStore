from django.db import migrations
from django.db.models import F


def populate_cache(apps, schema_editor):
    """
    Popula o cache inicial de livros
    """
    Livro = apps.get_model('core', 'Livro')
    NewLivroCache = apps.get_model('core', 'NewLivroCache')

    # Limpar cache existente
    NewLivroCache.objects.all().delete()

    # Popular com dados dos livros
    for livro in Livro.objects.all():
        NewLivroCache.objects.create(
            livro=livro,
            titulo=livro.titulo,
            autor=livro.autor,
            categoria=livro.categoria,
            classificacao=livro.classificacao,
            visualizacoes=livro.visualizacoes
        )


class Migration(migrations.Migration):
    replaces = [
        ('core', '0011_populate_livro_cache'),
        ('core', '0012_alter_newlivrorecomendado_options_and_more'),
    ]

    dependencies = [
        ('core',
         '0008_livrorecomendado_userpreferences_squashed_0010_remove_userpreferences_usuario_newlivrocache_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_cache,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterModelOptions(
            name='newlivrorecomendado',
            options={'verbose_name': 'Livro Recomendado', 'verbose_name_plural': 'Livros Recomendados'},
        ),
        # Outras operações da migração 0012 aqui...
    ]