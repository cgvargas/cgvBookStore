# core/views.py

from django.shortcuts import render, get_object_or_404
from .models import Livro

def index(request):
    livros = Livro.objects.all()
    return render(request, 'index.html', {'livros': livros})

def livro_detail(request, livro_id):
    livro = get_object_or_404(Livro, pk=livro_id)
    return render(request, 'livro_detail.html', {'livro': livro})

