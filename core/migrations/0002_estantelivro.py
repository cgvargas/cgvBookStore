# Generated by Django 5.1 on 2024-11-26 22:19

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstanteLivro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('livro_id', models.CharField(max_length=100)),
                ('tipo', models.CharField(choices=[('favorito', 'Favorito'), ('lendo', 'Lendo'), ('vou_ler', 'Vou ler'), ('lido', 'Lido')], max_length=20)),
                ('titulo', models.CharField(max_length=255)),
                ('autor', models.CharField(max_length=255)),
                ('capa', models.URLField()),
                ('data_lancamento', models.CharField(max_length=50)),
                ('sinopse', models.TextField()),
                ('data_adicao', models.DateTimeField(auto_now_add=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['titulo'],
            },
        ),
    ]