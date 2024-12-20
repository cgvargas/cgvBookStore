# core/presentation/admin/cache_admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta, datetime
from core.infrastructure.persistence.django.models import NewLivroCache


@admin.register(NewLivroCache)
class NewLivroCacheAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'titulo', 'autor', 'data_cache', 'cache_status')
    list_filter = (
        ('data_cache', admin.DateFieldListFilter),
    )
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
        if not obj.data_cache:
            return format_html(
                '<span style="color: red;">⚠ Sem data</span>'
            )

        # Verifica se a data é futura
        if obj.data_cache > timezone.now():
            return format_html(
                '<span style="color: orange;">⚠ Data futura</span>'
            )

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
        return False

    def get_queryset(self, request):
        """Sobrescreve queryset para filtrar datas futuras"""
        qs = super().get_queryset(request)
        now = timezone.now()
        return qs.filter(data_cache__lte=now)

    actions = ['limpar_cache_selecionados', 'corrigir_datas_futuras']

    @admin.action(description='Limpar cache dos itens selecionados')
    def limpar_cache_selecionados(self, request, queryset):
        from django.contrib import messages
        queryset.delete()
        messages.success(request, f'Cache limpo para {queryset.count()} livros.')

    @admin.action(description='Corrigir datas futuras')
    def corrigir_datas_futuras(self, request, queryset):
        from django.contrib import messages
        now = timezone.now()
        count = 0
        for item in queryset:
            if item.data_cache > now:
                item.data_cache = now
                item.save()
                count += 1
        messages.success(request, f'Corrigidas {count} datas futuras.')