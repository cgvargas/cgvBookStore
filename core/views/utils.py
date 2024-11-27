# utils.py
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.templatetags.static import static

def _processar_resultados_google_books(resultados):
    CAPA_PADRAO = static('images/capa-indisponivel.svg')

    livros_processados = []
    for item in resultados:
        imagem = item.get('imagem')
        if not imagem or imagem.strip() == '':
            imagem = CAPA_PADRAO

        livro = {
            'id': item.get('id', ''),
            'titulo': item.get('titulo', 'Título não disponível'),
            'autor': item.get('autor', 'Autor não disponível'),
            'descricao': item.get('descricao', 'Descrição não disponível'),
            'imagem': imagem,
            'data_publicacao': item.get('data_publicacao', 'Data não disponível'),
            'editora': item.get('editora', 'Editora não disponível'),
            'paginas': item.get('numero_paginas', 'Não disponível'),
            'categorias': item.get('categoria', 'Não categorizado'),
            'idioma': item.get('idioma', 'Não especificado'),
            'link': item.get('link', '#'),
            'isbn': item.get('isbn', 'ISBN não disponível'),
        }
        livros_processados.append(livro)
    return livros_processados

def _ordenar_resultados(livros, ordem):
    if ordem == 'title':
        return sorted(livros, key=lambda x: x['titulo'])
    elif ordem == 'date':
        return sorted(livros, key=lambda x: x['data_publicacao'], reverse=True)
    return livros

def _paginar_resultados(livros, pagina):
    paginator = Paginator(livros, 9)
    try:
        return paginator.page(pagina)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)