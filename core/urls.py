# core/urls.py

from django.urls import path
from .views import index, livro_detail

urlpatterns = [
    path('', index, name='index'),
    path('livro/<int:livro_id>/', livro_detail, name='livro_detail'),
]
