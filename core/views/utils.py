"""
Utilidades para processamento de resultados da API do Google Books.

Este módulo contém funções para processar, ordenar e paginar resultados
de livros obtidos da API do Google Books, padronizando o formato dos dados
e fornecendo funcionalidades de apresentação.
"""

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.templatetags.static import static
from django.utils.crypto import get_random_string


def _processar_resultados_google_books(resultados):
    """
    Processa e padroniza os resultados obtidos da API do Google Books.

    Transforma os dados brutos da API em um formato consistente,
    fornecendo valores padrão para campos ausentes e normalizando
    a estrutura dos dados.

    Args:
        resultados (list): Lista de dicionários contendo os dados brutos
            dos livros retornados pela API do Google Books.

    Returns:
        list: Lista de dicionários com os dados dos livros processados
            e padronizados, contendo os seguintes campos:
            - id (str): Identificador único do livro
            - titulo (str): Título do livro
            - autor (str): Nome do(s) autor(es)
            - descricao (str): Sinopse ou descrição do livro
            - imagem (str): URL da capa do livro ou imagem padrão
            - data_publicacao (str): Data de publicação
            - editora (str): Nome da editora
            - paginas (str): Número de páginas
            - categorias (str): Categorias/gêneros do livro
            - idioma (str): Idioma do livro
            - link (str): Link para mais informações
            - isbn (str): ISBN do livro
    """
    CAPA_PADRAO = static('images/capa-indisponivel.svg')

    livros_processados = []
    for item in resultados:
        # Garante que todos os campos necessários estejam presentes
        livro = {
            'id': item.get('id', ''),
            'titulo': item.get('titulo', 'Título não disponível'),
            'autor': item.get('autor', 'Autor não disponível'),
            'descricao': item.get('descricao', 'Descrição não disponível'),
            'imagem': item.get('imagem', CAPA_PADRAO),
            'data_publicacao': item.get('data_publicacao', 'Data não disponível'),
            'editora': item.get('editora', 'Editora não disponível'),
            'paginas': item.get('numero_paginas', 'Não disponível'),
            'categorias': item.get('categoria', 'Não categorizado'),
            'idioma': item.get('idioma', 'Não especificado'),
            'link': item.get('link', '#'),
            'isbn': item.get('isbn', 'ISBN não disponível'),
            # Campos adicionais garantidos
            'numero_paginas': item.get('numero_paginas', 'Não disponível'),
            'data_publicacao_completa': item.get('publicado_em', ''),
            'subtitulo': item.get('subtitulo', ''),
            'preview': item.get('preview', '#'),
            'volume_info': item.get('volume_info', {}),
            'sale_info': item.get('sale_info', {})
        }
        livros_processados.append(livro)
    return livros_processados


def _ordenar_resultados(livros, ordem):
    """
    Ordena uma lista de livros segundo o critério especificado.

    Args:
        livros (list): Lista de dicionários contendo dados dos livros
        ordem (str): Critério de ordenação, podendo ser:
            - 'title': ordena alfabeticamente por título
            - 'date': ordena por data de publicação (mais recente primeiro)
            - qualquer outro valor: mantém a ordem original

    Returns:
        list: Lista de livros ordenada segundo o critério especificado
    """
    if ordem == 'title':
        return sorted(livros, key=lambda x: x['titulo'])
    elif ordem == 'date':
        return sorted(livros, key=lambda x: x['data_publicacao'], reverse=True)
    return livros


def _paginar_resultados(livros, pagina):
    """
    Implementa paginação para uma lista de livros.

    Divide a lista de livros em páginas de 9 itens cada,
    tratando casos especiais como páginas inválidas.

    Args:
        livros (list): Lista de dicionários contendo dados dos livros
        pagina (int): Número da página desejada

    Returns:
        Page: Objeto Page do Django contendo os resultados paginados.
            Em caso de página inválida, retorna a primeira página.
            Em caso de página vazia, retorna a última página disponível.
    """
    paginator = Paginator(livros, 9)
    try:
        return paginator.page(pagina)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def safe_cache_key(key):
    """Gera uma chave de cache segura removendo caracteres problemáticos"""
    random_suffix = get_random_string(8)
    return f"{random_suffix}_{(''.join(c for c in key if c.isalnum() or c in '-_'))}"

