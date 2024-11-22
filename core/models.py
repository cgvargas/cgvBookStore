# core/models.py
from django.db import models


class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    descricao = models.TextField()
    data_publicacao = models.DateField()
    imagem = models.ImageField(upload_to='imagens/', default='imagens/default.jpg')
    downloads = models.IntegerField(default=0)
    destaque = models.BooleanField(default=False)
    mais_vendido = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo


class URLExterna(models.Model):
    nome = models.CharField(max_length=200)
    url = models.URLField()
    imagem = models.ImageField(upload_to='imagens/', default='imagens/default.jpg')  # Adiciona um campo para a imagem

    def __str__(self):
        return self.nome


class VideoYouTube(models.Model):
    titulo = models.CharField(max_length=200)
    url = models.URLField()
    imagem = models.URLField()  # Adiciona um campo para a URL da imagem

    def __str__(self):
        return self.titulo


class Contato(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    data = models.DateTimeField(auto_now_add=True)  # auto_now_add preenche automaticamente com a data e hora atuais

    def __str__(self):
        return f'{self.nome} - {self.assunto}'

