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

    def _create_cache_key(self, prefix: str, *args) -> str:
        """Cria uma chave de cache segura."""
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

            # Log detalhado das informações de venda
            logger.debug(f"Sale Info: {sale_info}")

            # Processa informações da imagem
            imagens = volume_info.get('imageLinks', {})
            imagem_url = (imagens.get('thumbnail') or
                          imagens.get('smallThumbnail') or
                          'https://via.placeholder.com/128x196')
            imagem_url = imagem_url.replace('http://', 'https://')

            # Processamento detalhado do preço
            preco = None
            moeda = 'BRL'
            if sale_info.get('saleability') == 'FOR_SALE':
                retail_price = sale_info.get('retailPrice', {})
                list_price = sale_info.get('listPrice', {})

                if retail_price:
                    preco = retail_price.get('amount')
                    moeda = retail_price.get('currencyCode', 'BRL')
                    logger.debug(f"Usando retail price: {preco} {moeda}")
                elif list_price:
                    preco = list_price.get('amount')
                    moeda = list_price.get('currencyCode', 'BRL')
                    logger.debug(f"Usando list price: {preco} {moeda}")

            processed_data = {
                'id': item.get('id'),
                'titulo': volume_info.get('title', 'Título não disponível'),
                'autor': ', '.join(volume_info.get('authors', ['Autor não disponível'])),
                'editora': volume_info.get('publisher', 'Editora não disponível'),
                'data_publicacao': volume_info.get('publishedDate', 'Data não disponível'),
                'descricao': volume_info.get('description', 'Descrição não disponível'),
                'isbn': ', '.join(
                    isbn.get('identifier', '')
                    for isbn in volume_info.get('industryIdentifiers', [])
                    if isbn.get('type') in ['ISBN_10', 'ISBN_13']
                ),
                'numero_paginas': str(volume_info.get('pageCount', 'Não disponível')),
                'categoria': ', '.join(volume_info.get('categories', ['Não categorizado'])),
                'idioma': volume_info.get('language', 'Não especificado'),
                'imagem': imagem_url,
                'preco': preco,
                'moeda': moeda,
                'link': volume_info.get('infoLink', '#'),
                'averageRating': volume_info.get('averageRating', 0),
                'ratingsCount': volume_info.get('ratingsCount', 0),
                'disponivel_venda': sale_info.get('saleability') == 'FOR_SALE',
                'ebook': sale_info.get('isEbook', False)
            }

            logger.debug(f"Dados processados: {processed_data}")
            return processed_data

        except Exception as e:
            logger.error(f"Erro ao processar resultado: {str(e)}")
            return None

    def buscar_livros(self, query: str, tipo_busca: str) -> List[Dict[str, Any]]:
        try:
            # Criar chave de cache segura
            cache_key = self._create_cache_key('books_search', tipo_busca, query)

            # Tenta recuperar do cache do Django (memória)
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Resultados recuperados do cache para '{query}'")
                return cached_result

            # Monta a query de acordo com o tipo de busca
            search_query = f'intitle:{query}' if tipo_busca == 'titulo' else f'inauthor:{query}'

            # Parâmetros da requisição
            params = {
                'q': search_query,
                'key': self.api_key,
                'maxResults': 40,
                'langRestrict': 'pt',
            }

            # Faz a requisição
            result = self._make_request(self.base_url, params)

            if not result or 'items' not in result:
                logger.warning(f"Nenhum resultado encontrado para '{query}'")
                return []

            # Processa os resultados
            livros = []
            for item in result['items']:
                try:
                    livro = self._processar_resultado(item)  # Agora usando o método correto
                    if livro:
                        livros.append(livro)
                        try:
                            LivroCache.salvar_book(item['id'], livro)
                        except Exception as e:
                            logger.warning(f"Não foi possível salvar no cache do banco: {str(e)}")
                except Exception as e:
                    logger.error(f"Erro ao processar livro: {str(e)}")
                    continue

            # Salva no cache do Django
            cache.set(cache_key, livros, timeout=86400)  # 24 horas

            return livros
        except Exception as e:
            logger.error(f"Erro na busca de livros: {str(e)}")
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