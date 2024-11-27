# __init__.py
from .auth_views import CustomLoginView, CustomLogoutView, register, check_username
from .book_views import livro_detail, buscar_livro, google_book_detail, adicionar_estante
from .profile_views import profile
from .general_views import index, sobre, contato, politica_privacidade, termos_uso

__all__ = [
    'CustomLoginView',
    'CustomLogoutView',
    'register',
    'check_username',
    'livro_detail',
    'buscar_livro',
    'google_book_detail',
    'adicionar_estante',
    'profile',
    'index',
    'sobre',
    'contato',
    'politica_privacidade',
    'termos_uso',
]