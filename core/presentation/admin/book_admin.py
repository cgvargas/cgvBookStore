# core/presentation/admin/book_admin.py
from django.contrib import admin
from django.utils.html import format_html
from core.models import Livro, LivroCache


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'exibir_imagem', 'visualizacoes', 'destaque',
                    'mais_vendido', 'classificacao_display')
    list_filter = ('destaque', 'mais_vendido', 'categoria', 'classificacao')
    search_fields = ('titulo', 'autor', 'descricao')
    ordering = ('titulo', 'autor')
    readonly_fields = ('visualizacoes',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'autor', 'descricao', 'categoria')
        }),
        ('Detalhes', {
            'fields': ('data_publicacao', 'imagem', 'classificacao')
        }),
        ('Status', {
            'fields': ('destaque', 'mais_vendido', 'visualizacoes')
        }),
    )

    def exibir_imagem(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="50" height="70" />', obj.imagem.url)
        return "Sem imagem"

    exibir_imagem.short_description = 'Capa'

    def classificacao_display(self, obj):
        if obj.classificacao:
            stars = '⭐' * obj.classificacao
            return format_html('<div title="{}">{}</div>',
                               f'{obj.classificacao} estrelas', stars)
        return '-'

    classificacao_display.short_description = 'Classificação'


@admin.register(LivroCache)
class LivroCacheAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'titulo', 'autor', 'data_cache', 'cache_status')
    list_filter = ('data_cache',)
    search_fields = ('book_id', 'titulo', 'autor', 'isbn')
    readonly_fields = ('data_cache',)

    fieldsets = (
        ('Identificação', {
            'fields': ('book_id', 'titulo', 'autor')
        }),
        ('Detalhes do Livro', {
            'fields': ('editora', 'data_publicacao', 'descricao', 'isbn',
                       'numero_paginas', 'categoria', 'idioma')
        }),
        ('Informações Comerciais', {
            'fields': ('imagem_url', 'preco')
        }),
        ('Metadados do Cache', {
            'fields': ('data_cache', 'dados_json'),
            'classes': ('collapse',)
        }),
    )

    def cache_status(self, obj):
        """Indica se o cache está atualizado (menos de 7 dias)"""
        from django.utils import timezone
        from datetime import timedelta

        idade_cache = timezone.now() - obj.data_cache
        if idade_cache <= timedelta(days=7):
            return format_html(
                '<span style="color: green;">✓ Atualizado</span>'
            )
        return format_html(
            '<span style="color: red;">⚠ Desatualizado</span>'
        )

    cache_status.short_description = 'Status do Cache'

    def has_add_permission(self, request):
        # Cache é gerenciado automaticamente
        return False

    actions = ['limpar_cache_selecionados']

    @admin.action(description='Limpar cache dos itens selecionados')
    def limpar_cache_selecionados(self, request, queryset):
        from django.contrib import messages
        queryset.delete()
        messages.success(request, f'Cache limpo para {queryset.count()} livros.')