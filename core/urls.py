# core/urls.py
from django.urls import path
from .views import CustomLogoutView, index, sobre, contato, livro_detail, profile, CustomLoginView, buscar_livro, \
    detalhe_livro, politica_privacidade, termos_uso, register

urlpatterns = [
    path('', index, name='index'),
    path('sobre/', sobre, name='sobre'),
    path('contato/', contato, name='contato'),
    path('livro/<int:livro_id>/', livro_detail, name='livro_detail'),
    path('profile/', profile, name='profile'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('buscar/', buscar_livro, name='buscar_livro'),
    path('livro/<str:livro_id>/', detalhe_livro, name='detalhe_livro'),
    path('politica-privacidade/', politica_privacidade, name='politica_privacidade'),
    path('termos-uso/', termos_uso, name='termos_uso'),
    path('register/', register, name='register'),
]
