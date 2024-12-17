# core/infrastructure/persistence/django/migrations/xxxx_recommendation_system.py

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):
    dependencies = [
        ('core', 'previous_migration'),  # Ajuste para sua última migração
    ]

    operations = [
        # 1. Criar novos modelos com nomes temporários
        migrations.CreateModel(
            name='NewLivroRecomendado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('livro_id', models.CharField(max_length=100)),
                ('titulo', models.CharField(max_length=255)),
                ('autor', models.CharField(max_length=255)),
                ('categoria', models.CharField(max_length=100, blank=True)),
                ('score', models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.0'))),
                ('data_recomendacao', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.CustomUser',
                    related_name='new_recommendations'
                )),
            ],
            options={
                'verbose_name': 'Livro Recomendado',
                'verbose_name_plural': 'Livros Recomendados',
                'db_table': 'core_new_livro_recomendado',
                'ordering': ['-score', 'titulo'],
            },
        ),
        migrations.CreateModel(
            name='NewUserPreferences',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('categorias_favoritas', models.JSONField(default=dict)),
                ('autores_favoritos', models.JSONField(default=dict)),
                ('ultima_atualizacao', models.DateTimeField(auto_now=True)),
                ('usuario', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='core.CustomUser',
                    related_name='new_preferences'
                )),
            ],
            options={
                'verbose_name': 'Preferência do Usuário',
                'verbose_name_plural': 'Preferências dos Usuários',
                'db_table': 'core_new_user_preferences',
            },
        ),

        # 2. Adicionar índices para otimização
        migrations.AddIndex(
            model_name='NewLivroRecomendado',
            index=models.Index(fields=['usuario', 'score'], name='idx_new_recom_user_score'),
        ),

        # 3. Renomear modelos para nomes finais
        migrations.RenameModel(
            old_name='NewLivroRecomendado',
            new_name='LivroRecomendado',
        ),
        migrations.RenameModel(
            old_name='NewUserPreferences',
            new_name='UserPreferences',
        ),

        # 4. Renomear tabelas para nomes finais
        migrations.AlterModelTable(
            name='LivroRecomendado',
            table='core_livro_recomendado',
        ),
        migrations.AlterModelTable(
            name='UserPreferences',
            table='core_user_preferences',
        ),
    ]