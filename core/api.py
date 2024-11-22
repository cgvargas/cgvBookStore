import requests
from decouple import config


def buscar_livro_google(query, tipo_busca):
    api_key = config('GOOGLE_BOOKS_API_KEY')  # Obtém a chave da api do arquivo .env
    url = 'https://www.googleapis.com/books/v1/volumes'

    # Montando a query de busca com base no tipo escolhido
    if tipo_busca == 'autor':
        search_query = f'inauthor:{query}'  # Busca por autor
    else:
        search_query = f'intitle:{query}'  # Busca por título

    params = {
        'q': search_query,
        'key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        resultados = response.json()
        if 'items' in resultados:
            return resultados['items']

    return []


def buscar_detalhes_livro(livro_id):
    api_key = config('GOOGLE_BOOKS_API_KEY')
    url = f'https://www.googleapis.com/books/v1/volumes/{livro_id}'

    params = {
        'key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        volume_info = data.get('volumeInfo', {})
        livro = {
            'titulo': volume_info.get('title', 'Título não disponível'),
            'autor': ', '.join(volume_info.get('authors', ['Autor não disponível'])),
            'editora': volume_info.get('publisher', 'Editora não disponível'),
            'data_publicacao': volume_info.get('publishedDate', 'Data de publicação não disponível'),
            'descricao': volume_info.get('description', 'Descrição não disponível'),
            'isbn': ', '.join([identifier['identifier'] for identifier in volume_info.get('industryIdentifiers', []) if identifier['type'] in ['ISBN_10', 'ISBN_13']]),
            'numero_paginas': volume_info.get('pageCount', 'Número de páginas não disponível'),
            'categoria': ', '.join(volume_info.get('categories', ['Categoria não disponível'])),
            'idioma': volume_info.get('language', 'Idioma não disponível'),
            'imagem': volume_info.get('imageLinks', {}).get('thumbnail', ''),
            'preco': data.get('saleInfo', {}).get('retailPrice', {}).get('amount', 'Preço não disponível')
        }
        return livro
    return None
