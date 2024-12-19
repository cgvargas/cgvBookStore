# core/infrastructure/persistence/django/migrations/xxxx_consolidate_recommendation_models.py
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_remove_userpreferences_usuario_newlivrocache_and_more'),  # Ajuste para sua última migration
    ]

    operations = [
        migrations.RenameModel(
            old_name='NewUserPreferences',
            new_name='UserPreferences',
        ),
        migrations.RenameModel(
            old_name='NewLivroRecomendado',
            new_name='LivroRecomendado',
        ),
    ]