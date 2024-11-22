# Generated by Django 5.1 on 2024-09-07 14:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_livro_downloads_livro_imagem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cadastro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=100)),
                ('telefone', models.CharField(help_text='Formato: (99)99999-9999', max_length=15, validators=[django.core.validators.RegexValidator(message='Número de telefone deve estar no formato: (99)99999-9999.', regex='^\\(\\d{2}\\)\\d{5}-\\d{4}$')])),
            ],
        ),
    ]