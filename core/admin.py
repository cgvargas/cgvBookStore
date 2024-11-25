# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Livro, URLExterna, VideoYouTube, CustomUser, LivroCache, Contato


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'nome_completo', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informações Adicionais', {'fields': ('nome_completo', 'email')}),
    )


class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'data_publicacao', 'destaque', 'mais_vendido')
    list_filter = ('destaque', 'mais_vendido')
    search_fields = ('titulo', 'autor')

class URLExternaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'url')
    search_fields = ('nome',)

class VideoYouTubeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'url')
    search_fields = ('titulo',)

admin.site.site_header = "Painel Administrativo CGVBookStore"
admin.site.site_title = "CGVBookStore"
admin.index_title = "Bem-vindo ao Painel Administrativo"
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Livro, LivroAdmin)
admin.site.register(LivroCache)
admin.site.register(Contato)
admin.site.register(URLExterna, URLExternaAdmin)
admin.site.register(VideoYouTube, VideoYouTubeAdmin)

