# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (Livro, URLExterna, VideoYouTube, CustomUser,
                    LivroCache, Contato, EstanteLivro, HistoricoAtividade)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'nome_completo', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'data_registro']
    search_fields = ['username', 'email', 'nome_completo']
    ordering = ['-data_registro']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo', 'profile_image')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo', 'email')}),
    )


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'data_publicacao', 'destaque', 'mais_vendido']
    list_filter = ['destaque', 'mais_vendido', 'data_publicacao']
    search_fields = ['titulo', 'autor', 'categoria']
    ordering = ['-data_publicacao']


@admin.register(URLExterna)
class URLExternaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'url']
    search_fields = ['nome', 'url']
    ordering = ['nome']


@admin.register(VideoYouTube)
class VideoYouTubeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'url']
    search_fields = ['titulo', 'url']
    ordering = ['titulo']


@admin.register(LivroCache)
class LivroCacheAdmin(admin.ModelAdmin):
    list_display = ['book_id', 'titulo', 'autor', 'data_cache']
    list_filter = ['data_cache']
    search_fields = ['book_id', 'titulo', 'autor', 'isbn']
    ordering = ['-data_cache']


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'assunto', 'data']
    list_filter = ['data']
    search_fields = ['nome', 'email', 'assunto', 'mensagem']
    ordering = ['-data']


@admin.register(EstanteLivro)
class EstanteLivroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'tipo', 'livro_id', 'data_adicao']
    list_filter = ['tipo', 'data_adicao']
    search_fields = ['titulo', 'usuario__username', 'livro_id']
    ordering = ['-data_adicao']


@admin.register(HistoricoAtividade)
class HistoricoAtividadeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'acao', 'titulo_livro', 'data']
    list_filter = ['acao', 'data']
    search_fields = ['usuario__username', 'titulo_livro']
    date_hierarchy = 'data'


# Configurações do site admin
admin.site.site_header = "Painel Administrativo CGVBookStore"
admin.site.site_title = "CGVBookStore"
admin.site.index_title = "Bem-vindo ao Painel Administrativo"