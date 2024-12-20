# core/migrations/0013_alter_model_options.py

from django.db import migrations


def forwards_func(apps, schema_editor):
    # Obtém a conexão
    connection = schema_editor.connection

    # Obter lista de índices
    cursor = connection.cursor()

    # Para SQLite, isso lista todos os índices
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='index' 
        AND sql IS NOT NULL 
        AND tbl_name='core_newlivrorecomendado';
    """)

    # Remove cada índice encontrado
    for (index_name,) in cursor.fetchall():
        cursor.execute(f"DROP INDEX IF EXISTS {index_name};")


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_populate_livro_cache_squashed_0012_alter_newlivrorecomendado_options_and_more'),
    ]

    operations = [
        # Primeiro limpa todos os índices
        migrations.RunPython(forwards_func, migrations.RunPython.noop),

        # Depois aplica as novas configurações
        migrations.AlterModelOptions(
            name='newlivrorecomendado',
            options={
                'ordering': ['-score', 'titulo'],
                'verbose_name': 'Livro Recomendado',
                'verbose_name_plural': 'Livros Recomendados'
            },
        ),
        migrations.AlterModelOptions(
            name='newuserpreferences',
            options={
                'verbose_name': 'Preferência do Usuário',
                'verbose_name_plural': 'Preferências dos Usuários'
            },
        ),
    ]