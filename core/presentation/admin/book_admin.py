# core/presentation/admin/book_admin.py
from django.contrib import admin
from django.utils.html import format_html
from core.models import Livro


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