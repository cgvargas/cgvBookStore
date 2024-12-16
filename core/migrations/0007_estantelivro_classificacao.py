# Generated by Django 5.1.1 on 2024-12-07 21:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_livro_classificacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='estantelivro',
            name='classificacao',
            field=models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1, 'A classificação deve ser de pelo menos 1 estrela'), django.core.validators.MaxValueValidator(5, 'A classificação não pode ser maior que 5 estrelas')], verbose_name='Classificação'),
        ),
    ]
