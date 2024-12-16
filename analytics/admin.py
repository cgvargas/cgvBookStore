from django.contrib import admin
from .models import (
    SiteAnalytics, PageView, BookAnalytics, 
    SearchAnalytics, UserActivityLog, ErrorLog,
    AnalyticsSettings
)

@admin.register(SiteAnalytics)
class SiteAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('data', 'visitas_total', 'visitas_autenticadas', 
                   'visitas_anonimas', 'usuarios_ativos')
    list_filter = ['data']
    date_hierarchy = 'data'
    ordering = ('-data',)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('url', 'usuario', 'timestamp', 'sessao_id', 'tempo_na_pagina')
    list_filter = ['timestamp', 'dispositivo']
    search_fields = ['url', 'usuario__username', 'sessao_id']
    date_hierarchy = 'timestamp'

@admin.register(BookAnalytics)
class BookAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('livro', 'visualizacoes', 'compartilhamentos_facebook',
                   'compartilhamentos_twitter', 'compartilhamentos_whatsapp',
                   'adicoes_estante', 'data')
    list_filter = ['data']
    search_fields = ['livro']
    date_hierarchy = 'data'

@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('termo_busca', 'tipo_busca', 'resultados_encontrados',
                   'usuario', 'timestamp', 'foi_bem_sucedida')
    list_filter = ['timestamp', 'tipo_busca', 'foi_bem_sucedida']
    search_fields = ['termo_busca', 'usuario__username']
    date_hierarchy = 'timestamp'

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'acao', 'timestamp', 'ip_address', 'secao_atual')
    list_filter = ['timestamp', 'acao']
    search_fields = ['usuario__username', 'ip_address']
    date_hierarchy = 'timestamp'

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'tipo_erro', 'usuario', 'url')
    list_filter = ['timestamp', 'tipo_erro']
    search_fields = ['mensagem', 'traceback', 'usuario__username']
    date_hierarchy = 'timestamp'

@admin.register(AnalyticsSettings)
class AnalyticsSettingsAdmin(admin.ModelAdmin):
    list_display = ('tracking_enabled', 'data_retention', 'daily_report',
                   'alert_threshold', 'notification_email', 'last_cleanup')
    list_filter = ['tracking_enabled', 'daily_report']
    readonly_fields = ['created_at', 'updated_at']