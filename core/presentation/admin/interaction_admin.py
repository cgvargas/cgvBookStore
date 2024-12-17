# core/presentation/admin/interaction_admin.py
from django.contrib import admin
from django.utils.html import format_html
from core.models import Contato, EstanteLivro, HistoricoAtividade

@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'assunto', 'data', 'status_mensagem']
    list_filter = ['data', 'assunto']
    search_fields = ['nome', 'email', 'assunto', 'mensagem']
    ordering = ['-data']
    readonly_fields = ['data']

    def status_mensagem(self, obj):
        return format_html(
            '<span style="color: green;">●</span> Recebida'
            if obj.data else
            '<span style="color: gray;">○</span> Pendente'
        )
    status_mensagem.short_description = 'Status'

@admin.register(EstanteLivro)
class EstanteLivroAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'titulo', 'tipo', 'exibir_capa', 'classificacao_display', 'data_adicao']
    list_filter = ['tipo', 'manual', 'data_adicao', 'classificacao']
    search_fields = ['titulo', 'usuario__username', 'livro_id', 'autor']
    ordering = ['-data_adicao']
    readonly_fields = ['data_adicao', 'ultima_atualizacao']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('usuario', 'tipo', 'titulo', 'autor', 'capa')
        }),
        ('Detalhes do Livro', {
            'fields': ('livro_id', 'manual', 'editora', 'data_lancamento',
                      'numero_paginas', 'isbn', 'idioma', 'categoria')
        }),
        ('Avaliação e Notas', {
            'fields': ('classificacao', 'notas_pessoais')
        }),
        ('Metadados', {
            'fields': ('data_adicao', 'ultima_atualizacao'),
            'classes': ('collapse',)
        })
    )

    def exibir_capa(self, obj):
        if obj.tem_capa:
            return format_html('<img src="{}" width="40" height="60" />', obj.capa)
        return "Sem capa"
    exibir_capa.short_description = 'Capa'

    def classificacao_display(self, obj):
        if obj.classificacao:
            stars = '⭐' * obj.classificacao
            return format_html('<div title="{}">{}</div>',
                             f'{obj.classificacao} estrelas', stars)
        return '-'
    classificacao_display.short_description = 'Classificação'

@admin.register(HistoricoAtividade)
class HistoricoAtividadeAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'acao', 'titulo_livro', 'data', 'exibir_detalhes']
    list_filter = ['acao', 'data']
    search_fields = ['usuario__username', 'titulo_livro', 'detalhes']
    date_hierarchy = 'data'
    readonly_fields = ['data']

    def exibir_detalhes(self, obj):
        return format_html(
            '<span title="{}">{}</span>',
            obj.detalhes,
            obj.detalhes[:50] + '...' if len(obj.detalhes) > 50 else obj.detalhes
        )
    exibir_detalhes.short_description = 'Detalhes'