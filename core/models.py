# core/models.py
import decimal

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import logging
import json


logger = logging.getLogger(__name__)

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    descricao = models.TextField()
    data_publicacao = models.DateField()
    imagem = models.ImageField(upload_to='imagens/', default='imagens/default.jpg')
    downloads = models.IntegerField(default=0)
    destaque = models.BooleanField(default=False)
    mais_vendido = models.BooleanField(default=False)
    categoria = models.CharField(max_length=100, blank=True, null=True)  # Novo campo

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return self.titulo


class LivroCache(models.Model):
    book_id = models.CharField(max_length=200, unique=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    editora = models.CharField(max_length=200, null=True, blank=True)
    data_publicacao = models.CharField(max_length=50, null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)
    isbn = models.CharField(max_length=50, null=True, blank=True)
    numero_paginas = models.CharField(max_length=50, null=True, blank=True)
    categoria = models.CharField(max_length=200, null=True, blank=True)
    idioma = models.CharField(max_length=50, null=True, blank=True)
    imagem_url = models.URLField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data_cache = models.DateTimeField(auto_now=True)
    dados_json = models.TextField(null=True, blank=True)  # Campo para armazenar dados extras em JSON

    class Meta:
        indexes = [
            models.Index(fields=['book_id', 'data_cache']),
        ]
        verbose_name = 'Cache de Livro'
        verbose_name_plural = 'Cache de Livros'

    @classmethod
    def get_book(cls, book_id):
        """Busca um livro no cache com fallback para diferentes níveis de cache."""
        # Primeiro tenta o cache do Django
        cache_key = f"book_detail:{book_id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Livro {book_id} recuperado do cache Django")
            return cached_data

        # Se não encontrou no cache do Django, tenta no banco
        try:
            cache_threshold = timezone.now() - timedelta(days=7)
            cached_book = cls.objects.select_related().get(
                book_id=book_id,
                data_cache__gte=cache_threshold
            )

            # Constrói o dicionário de retorno
            book_data = {
                'id': cached_book.book_id,
                'titulo': cached_book.titulo,
                'autor': cached_book.autor,
                'editora': cached_book.editora,
                'data_publicacao': cached_book.data_publicacao,
                'descricao': cached_book.descricao,
                'isbn': cached_book.isbn,
                'numero_paginas': cached_book.numero_paginas,
                'categoria': cached_book.categoria,
                'idioma': cached_book.idioma,
                'imagem': cached_book.imagem_url,
                'preco': str(cached_book.preco) if cached_book.preco else None,
            }

            # Adiciona dados extras do JSON se existirem
            if cached_book.dados_json:
                try:
                    extra_data = json.loads(cached_book.dados_json)
                    book_data.update(extra_data)
                except json.JSONDecodeError:
                    logger.error(f"Erro ao decodificar dados JSON para livro {book_id}")

            # Salva no cache do Django para próximas requisições
            cache.set(cache_key, book_data, timeout=86400)  # 24 horas

            logger.info(f"Livro {book_id} recuperado do banco de dados e salvo no cache")
            return book_data

        except cls.DoesNotExist:
            logger.info(f"Livro {book_id} não encontrado em nenhum cache")
            return None
        except Exception as e:
            logger.error(f"Erro ao recuperar livro {book_id} do cache: {str(e)}")
            return None

    @classmethod
    def salvar_book(cls, book_id, dados_livro):
        """Salva um livro no cache com suporte a dados extras."""
        try:
            # Separa os dados principais dos extras
            dados_principais = {
                'titulo': dados_livro.get('titulo', ''),
                'autor': dados_livro.get('autor', ''),
                'editora': dados_livro.get('editora', ''),
                'data_publicacao': dados_livro.get('data_publicacao', ''),
                'descricao': dados_livro.get('descricao', ''),
                'isbn': dados_livro.get('isbn', ''),
                'numero_paginas': dados_livro.get('numero_paginas', ''),
                'categoria': dados_livro.get('categoria', ''),
                'idioma': dados_livro.get('idioma', ''),
                'imagem_url': dados_livro.get('imagem', ''),
                'preco': dados_livro.get('preco', 0.0) if dados_livro.get('preco') is not None else 0.0,
            }

            # Log do preço antes de salvar
            logger.debug(f"Preço a ser salvo para o livro {book_id}: {dados_principais['preco']}")

            # Dados extras vão para o campo JSON
            dados_extras = {
                k: v for k, v in dados_livro.items()
                if k not in dados_principais.keys() and k != 'id'
            }

            # Cria ou atualiza o registro
            obj, created = cls.objects.update_or_create(
                book_id=book_id,
                defaults={
                    **dados_principais,
                    'dados_json': json.dumps(dados_extras) if dados_extras else None
                }
            )

            # Salva também no cache do Django
            cache_key = f"book_detail:{book_id}"
            cache.set(cache_key, dados_livro, timeout=86400)  # 24 horas

            logger.info(f"Livro {book_id} {'criado' if created else 'atualizado'} no cache")
            return obj

        except Exception as e:
            logger.error(f"Erro ao salvar livro {book_id} no cache: {str(e)}")
            return None

    def clean_cache(self):
        """Limpa caches antigos."""
        try:
            cache_threshold = timezone.now() - timedelta(days=7)
            old_caches = LivroCache.objects.filter(data_cache__lt=cache_threshold)
            count = old_caches.count()
            old_caches.delete()
            logger.info(f"Removidos {count} registros antigos do cache")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")

    def __str__(self):
        return f"Cache: {self.titulo} ({self.book_id})"

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


class CustomUser(AbstractUser):
    nome_completo = models.CharField(max_length=255, verbose_name="Nome Completo")
    data_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        # Adicione isto para garantir o nome correto da tabela
        db_table = 'core_customuser'

    def __str__(self):
        return self.username

