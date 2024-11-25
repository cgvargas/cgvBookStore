# Generated by Django 5.1 on 2024-11-25 19:49

import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('assunto', models.CharField(max_length=200)),
                ('mensagem', models.TextField()),
                ('data', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Livro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('autor', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('data_publicacao', models.DateField()),
                ('imagem', models.ImageField(default='imagens/default.jpg', upload_to='imagens/')),
                ('downloads', models.IntegerField(default=0)),
                ('destaque', models.BooleanField(default=False)),
                ('mais_vendido', models.BooleanField(default=False)),
                ('categoria', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'Livro',
                'verbose_name_plural': 'Livros',
            },
        ),
        migrations.CreateModel(
            name='URLExterna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('imagem', models.ImageField(default='imagens/default.jpg', upload_to='imagens/')),
            ],
        ),
        migrations.CreateModel(
            name='VideoYouTube',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('imagem', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('nome_completo', models.CharField(max_length=255, verbose_name='Nome Completo')),
                ('data_registro', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
                'db_table': 'core_customuser',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='LivroCache',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.CharField(max_length=200, unique=True)),
                ('titulo', models.CharField(max_length=200)),
                ('autor', models.CharField(max_length=200)),
                ('editora', models.CharField(blank=True, max_length=200, null=True)),
                ('data_publicacao', models.CharField(blank=True, max_length=50, null=True)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('isbn', models.CharField(blank=True, max_length=50, null=True)),
                ('numero_paginas', models.CharField(blank=True, max_length=50, null=True)),
                ('categoria', models.CharField(blank=True, max_length=200, null=True)),
                ('idioma', models.CharField(blank=True, max_length=50, null=True)),
                ('imagem_url', models.URLField(blank=True, null=True)),
                ('preco', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('data_cache', models.DateTimeField(auto_now=True)),
                ('dados_json', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Cache de Livro',
                'verbose_name_plural': 'Cache de Livros',
                'indexes': [models.Index(fields=['book_id', 'data_cache'], name='core_livroc_book_id_231eb4_idx')],
            },
        ),
    ]
