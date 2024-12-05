# core/api.py
from django.core.cache import cache
import requests
import logging
import hashlib
from decouple import config
from typing import Optional, List, Dict, Any
from .models import LivroCache

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GoogleBooksAPI:
    def __init__(self):
        self.api_key = config('GOOGLE_BOOKS_API_KEY')
        self.base_url = 'https://www.googleapis.com/books/v1/volumes'
        self.session = requests.Session()
        # Configura retry e timeout padrão na sessão
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=100,
            pool_maxsize=100
        ))

    def _create_cache_key(self, prefix: str, *args) -> str:
        """
        Cria uma chave de cache segura usando MD5.

        Args:
            prefix (str): Prefixo para a chave (ex: 'books_search', 'book_detail')
            *args: Argumentos variáveis que serão usados para compor a chave

        Returns:
            str: Hash MD5 que representa a chave de cache
        """
        key_parts = [str(arg).replace(' ', '_') for arg in args]
        raw_key = f"{prefix}_{'_'.join(key_parts)}"
        return hashlib.md5(raw_key.encode('utf-8')).hexdigest()

    def _make_request(self, url: str, params: Dict[str, str]) -> Optional[Dict]:
        """Faz a requisição para a API com tratamento de erros."""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Erro ao processar JSON: {str(e)}")
            return None

    def _processar_resultado(self, item: Dict) -> Optional[Dict[str, Any]]:
        """Processa um resultado da API em um formato padronizado."""
        try:
            volume_info = item.get('volumeInfo', {})
            sale_info = item.get('saleInfo', {})

            # Processa informações da imagem com HTTPS
            imagens = volume_info.get('imageLinks', {})
            imagem_url = (
                imagens.get('thumbnail') or
                imagens.get('smallThumbnail') or
                '/static/images/capa-indisponivel.svg'
            )
            imagem_url = imagem_url.replace('http://', 'https://')

            # Processamento mais robusto da data
            data_publicacao = volume_info.get('publishedDate', '')
            if data_publicacao:
                try:
                    # Tenta pegar apenas o ano se a data estiver completa
                    data_publicacao = data_publicacao.split('-')[0]
                except Exception:
                    pass

            # Processamento de ISBN mais eficiente
            isbns = volume_info.get('industryIdentifiers', [])
            isbn = next(
                (isbn['identifier'] for isbn in isbns
                 if isbn.get('type') in ['ISBN_13', 'ISBN_10']),
                'ISBN não disponível'
            )

            # Processamento de preço com conversão segura
            preco = None
            moeda = 'BRL'
            if sale_info.get('saleability') == 'FOR_SALE':
                retail_price = sale_info.get('retailPrice') or sale_info.get('listPrice', {})
                if retail_price:
                    try:
                        preco = float(retail_price.get('amount', 0))
                        moeda = retail_price.get('currencyCode', 'BRL')
                    except (ValueError, TypeError):
                        logger.warning(f"Erro ao converter preço para {item.get('id')}")

            # Extração segura de categorias
            categorias = volume_info.get('categories', [])
            if isinstance(categorias, list):
                categoria = ', '.join(categorias)
            else:
                categoria = str(categorias)

            processed_data = {
                'id': item.get('id'),
                'titulo': volume_info.get('title', 'Título não disponível'),
                'autor': ', '.join(volume_info.get('authors', ['Autor não disponível'])),
                'editora': volume_info.get('publisher', 'Editora não disponível'),
                'data_publicacao': data_publicacao or 'Data não disponível',
                'descricao': volume_info.get('description', 'Descrição não disponível'),
                'isbn': isbn,
                'numero_paginas': str(volume_info.get('pageCount', 'Não disponível')),
                'categoria': categoria,
                'idioma': volume_info.get('language', 'Não especificado'),
                'imagem': imagem_url,
                'preco': preco,
                'moeda': moeda,
                'link': volume_info.get('infoLink', '#'),
                'averageRating': float(volume_info.get('averageRating', 0)),
                'ratingsCount': int(volume_info.get('ratingsCount', 0)),
                'disponivel_venda': sale_info.get('saleability') == 'FOR_SALE',
                'ebook': sale_info.get('isEbook', False),
                'preview': volume_info.get('previewLink', '#'),
                'paginas': volume_info.get('pageCount', 0),
                'subtitulo': volume_info.get('subtitle', ''),
                'publicado_em': data_publicacao
            }

            # Remove valores None para economizar cache
            return {k: v for k, v in processed_data.items() if v is not None}

        except Exception as e:
            logger.error(f"Erro ao processar resultado: {str(e)}", exc_info=True)
            return None

    def buscar_livros(self, query: str, tipo_busca: str, max_results: int = 40) -> List[Dict[str, Any]]:
        """
        Busca livros com parâmetros expandidos e melhor tratamento de erros.
        """
        try:
            cache_key = self._create_cache_key('books_search', tipo_busca, query, max_results)

            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result

            # Mapeamento de tipos de busca
            tipos_busca = {
                'titulo': 'intitle:',
                'autor': 'inauthor:',
                'editora': 'inpublisher:',
                'isbn': 'isbn:',
                'categoria': 'subject:',
                'todos': ''
            }

            prefixo = tipos_busca.get(tipo_busca, '')
            search_query = f"{prefixo}{query}" if prefixo else query

            params = {
                'q': search_query,
                'key': self.api_key,
                'maxResults': max_results,
                'langRestrict': 'pt',
                'orderBy': 'relevance',
                'printType': 'all'
            }

            result = self._make_request(self.base_url, params)
            if not result or 'items' not in result:
                return []

            livros = []
            for item in result['items']:
                livro = self._processar_resultado(item)
                if livro:
                    livros.append(livro)
                    try:
                        LivroCache.salvar_book(item['id'], livro)
                    except Exception as e:
                        logger.warning(f"Erro ao salvar no cache: {str(e)}")

            cache.set(cache_key, livros, timeout=86400)
            return livros

        except Exception as e:
            logger.error(f"Erro na busca de livros: {str(e)}", exc_info=True)
            return []

    def buscar_detalhes(self, livro_id: str) -> Optional[Dict[str, Any]]:
        """Busca detalhes de um livro específico."""
        try:
            cache_key = self._create_cache_key('book_detail', livro_id)

            cached_book = cache.get(cache_key)
            if cached_book:
                logger.info(f"Detalhes do livro {livro_id} recuperados do cache")
                return cached_book

            try:
                model_cached_book = LivroCache.get_book(livro_id)
                if model_cached_book:
                    cache.set(cache_key, model_cached_book, timeout=86400)
                    return model_cached_book
            except Exception as e:
                logger.warning(f"Erro ao acessar cache do banco: {str(e)}")

            url = f'{self.base_url}/{livro_id}'
            params = {'key': self.api_key}

            result = self._make_request(url, params)
            if not result:
                return None

            livro = self._processar_resultado(result)  # Agora usando o método correto
            if livro:
                try:
                    LivroCache.salvar_book(livro_id, livro)
                except Exception as e:
                    logger.warning(f"Não foi possível salvar no cache do banco: {str(e)}")

                cache.set(cache_key, livro, timeout=86400)

            return livro
        except Exception as e:
            logger.error(f"Erro ao buscar detalhes: {str(e)}")
            return None


# Instância global para uso em toda a aplicação
google_books_api = GoogleBooksAPI()