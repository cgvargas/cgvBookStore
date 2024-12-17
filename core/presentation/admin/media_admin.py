# core/presentation/admin/media_admin.py
from django.contrib import admin
from django.utils.html import format_html
from core.models import URLExterna, VideoYouTube

@admin.register(URLExterna)
class URLExternaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'exibir_url', 'exibir_imagem']
    search_fields = ['nome', 'url']
    ordering = ['nome']

    def exibir_url(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
    exibir_url.short_description = 'URL'

    def exibir_imagem(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="50" />', obj.imagem.url)
        return "Sem imagem"
    exibir_imagem.short_description = 'Imagem'

@admin.register(VideoYouTube)
class VideoYouTubeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'exibir_url', 'exibir_preview']
    search_fields = ['titulo', 'url']
    ordering = ['titulo']

    def exibir_url(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.url, obj.url)
    exibir_url.short_description = 'URL'

    def exibir_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" width="120" style="border-radius: 8px;" />',
                obj.imagem
            )
        return "Sem preview"
    exibir_preview.short_description = 'Preview'