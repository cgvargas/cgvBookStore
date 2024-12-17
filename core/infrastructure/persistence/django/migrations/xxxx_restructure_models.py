# core/infrastructure/persistence/django/migrations/xxxx_restructure_models.py

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0009_rename_downloads_livro_visualizacoes'),
    ]

    operations = [
        # 1. Criar os novos modelos
        migrations.CreateModel(
            name='NewLivroCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.CharField(max_length=200, unique=True)),
                ('titulo', models.CharField(max_length=200)),
                ('autor', models.CharField(max_length=200)),
                ('editora', models.CharField(max_length=200, null=True, blank=True)),
                ('data_publicacao', models.CharField(max_length=50, null=True, blank=True)),
                ('descricao', models.TextField(null=True, blank=True)),
                ('isbn', models.CharField(max_length=50, null=True, blank=True)),
                ('numero_paginas', models.CharField(max_length=50, null=True, blank=True)),
                ('categoria', models.CharField(max_length=200, null=True, blank=True)),
                ('idioma', models.CharField(max_length=50, null=True, blank=True)),
                ('imagem_url', models.URLField(null=True, blank=True)),
                ('preco', models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)),
                ('data_cache', models.DateTimeField(auto_now=True)),
                ('dados_json', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Cache de Livro',
                'verbose_name_plural': 'Cache de Livros',
            },
        ),
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
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.customuser')),
            ],
            options={
                'verbose_name': 'Livro Recomendado',
                'verbose_name_plural': 'Livros Recomendados',
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
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.customuser')),
            ],
            options={
                'verbose_name': 'Preferência do Usuário',
                'verbose_name_plural': 'Preferências dos Usuários',
            },
        ),
        # 2. Adicionar índices
        migrations.AddIndex(
            model_name='NewLivroCache',
            index=models.Index(fields=['book_id', 'data_cache'], name='idx_new_cache_book'),
        ),
        migrations.AddIndex(
            model_name='NewLivroRecomendado',
            index=models.Index(fields=['usuario', 'score'], name='idx_new_recom_score'),
        ),
    ]