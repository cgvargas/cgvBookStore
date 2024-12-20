# core/presentation/admin/__init__.py
from django.contrib import admin
from .book_admin import LivroAdmin
from .cache_admin import NewLivroCacheAdmin
from .user_admin import CustomUserAdmin
from .media_admin import URLExternaAdmin, VideoYouTubeAdmin
from .interaction_admin import ContatoAdmin, EstanteLivroAdmin, HistoricoAtividadeAdmin

# Configurações do site admin
admin.site.site_header = "Painel Administrativo CGVBookStore"
admin.site.site_title = "CGVBookStore"
admin.site.index_title = "Bem-vindo ao Painel Administrativo"