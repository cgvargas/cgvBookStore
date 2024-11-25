# core/urls.py
from django.urls import path
from .views import (
    CustomLogoutView,
    CustomLoginView,
    index,
    sobre,
    contato,
    profile,
    buscar_livro,
    google_book_detail,
    livro_detail,
    politica_privacidade,
    termos_uso,
    register,
    check_username
)

urlpatterns = [
    # Páginas principais
    path('', index, name='index'),
    path('sobre/', sobre, name='sobre'),
    path('contato/', contato, name='contato'),

    # Autenticação
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', register, name='register'),
    path('profile/', profile, name='profile'),
    path('check-username/', check_username, name='check_username'),

    # Livros locais
    path('livros/local/<int:livro_id>/', livro_detail, name='livro_detail'),

    # Google Books
    path('buscar/', buscar_livro, name='buscar_livro'),
    path('livros/google/<str:livro_id>/', google_book_detail, name='detalhe_livro'),

    # Páginas legais
    path('politica-privacidade/', politica_privacidade, name='politica_privacidade'),
    path('termos-uso/', termos_uso, name='termos_uso'),
]