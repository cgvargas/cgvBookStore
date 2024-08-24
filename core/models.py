# core/models.py

from django.db import models

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    descricao = models.TextField()
    data_publicacao = models.DateField()

    def __str__(self):
        return self.titulo

