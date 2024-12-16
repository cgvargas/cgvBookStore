# core/urls.py
from django.urls import path
from core.views import (
    CustomLogoutView, CustomLoginView,
    index, sobre,
    contato, buscar_livro,
    google_book_detail, livro_detail,
    politica_privacidade, termos_uso,
    register, check_username,
    book_actions, profile_views,
    recommendation_views, auth_views,
)
from core.presentation.views import recommendation_views as new_recommendation_views


urlpatterns = [
    # Páginas principais
    path('', index, name='index'),
    path('sobre/', sobre, name='sobre'),
    path('contato/', contato, name='contato'),

    # Autenticação
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('auto-logout/', auth_views.auto_logout, name='auto_logout'),
    path('register/', register, name='register'),
    path('check-username/', check_username, name='check_username'),

    # Livros locais
    path('livros/local/<int:livro_id>/', livro_detail, name='livro_detail'),

    # Google Books
    path('buscar/', buscar_livro, name='buscar_livro'),
    path('livros/google/<str:livro_id>/', google_book_detail, name='google_book_detail'),
    path('livros/adicionar/<str:livro_id>/', book_actions.adicionar_estante, name='adicionar_estante'),

    # Páginas legais
    path('politica-privacidade/', politica_privacidade, name='politica_privacidade'),
    path('termos-uso/', termos_uso, name='termos_uso'),

    # Ações de estante
    path('prateleira/<str:shelf_type>/livros/', book_actions.get_shelf_books, name='get_shelf_books'),
    path('livros/excluir/<int:livro_id>/', book_actions.excluir_livro, name='excluir_livro'),
    path('livros/transferir/<int:livro_id>/', book_actions.transferir_livro, name='transferir_livro'),

    # Perfil do usuário
    path('profile/', profile_views.profile, name='profile'),
    path('profile/update-photo/', profile_views.update_profile_photo, name='update_profile_photo'),
    path('profile/delete-photo/', profile_views.delete_profile_photo, name='delete_profile_photo'),
    path('profile/update/', profile_views.update_profile, name='update_profile'),
    path('adicionar-livro-manual/', profile_views.adicionar_livro_manual, name='adicionar_livro_manual'),
    path('verificar-livro-existente/', profile_views.verificar_livro_existente, name='verificar_livro_existente'),
    path('editar-livro-manual/<int:livro_id>/', profile_views.editar_livro_manual, name='editar_livro_manual'),
    path('livros/<int:livro_id>/detalhes/', profile_views.detalhes_livro, name='detalhes_livro'),
    path('livros/<int:livro_id>/classificar/', profile_views.salvar_classificacao, name='salvar_classificacao'),

    # URLs de recomendação
    path('perfil/recomendacoes/', recommendation_views.gerar_recomendacoes, name='recomendacoes_perfil'),
    path('api/preferencias/atualizar/', recommendation_views.atualizar_preferencias, name='atualizar_preferencias'),
    path('api/recomendacoes/obter/', recommendation_views.obter_recomendacoes_ajax, name='obter_recomendacoes'),
    path('api/debug-recomendacoes/', recommendation_views.debug_recomendacoes, name='debug_recomendacoes'),

    # Novas URLs com a nova estrutura
    path('api/v2/recommendations/', new_recommendation_views.get_recommendations, name='api_recommendations'),
    path('api/v2/recommendations/preferences/', new_recommendation_views.update_preferences, name='api_update_preferences'),

]