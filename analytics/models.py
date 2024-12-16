# analytics/models.py
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SiteAnalytics(models.Model):
    objects = models.Manager()
    data = models.DateField(default=timezone.now)
    visitas_total = models.IntegerField(default=0)
    visitas_anonimas = models.IntegerField(default=0)
    visitas_autenticadas = models.IntegerField(default=0)
    usuarios_ativos = models.IntegerField(default=0)
    novos_usuarios = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Análise do Site'
        verbose_name_plural = 'Análises do Site'
        get_latest_by = 'data'

    def __str__(self):
        return f"Analytics {self.data}"

    @classmethod
    def cleanup_old_data(cls):
        """Remove dados antigos"""
        settings = AnalyticsSettings.get_settings()
        cutoff_date = timezone.now() - timedelta(days=settings.data_retention)
        PageView.objects.filter(timestamp__lt=cutoff_date).delete()
        UserActivityLog.objects.filter(timestamp__lt=cutoff_date).delete()


class PageView(models.Model):
    """Modelo para rastrear visualizações de páginas"""
    objects = models.Manager()
    url = models.CharField(max_length=500)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    sessao_id = models.CharField(max_length=100)
    dispositivo = models.CharField(max_length=50)
    navegador = models.CharField(max_length=50)
    tempo_na_pagina = models.DurationField(null=True)


class BookAnalytics(models.Model):
    """Modelo para análise específica de livros"""
    objects = models.Manager()
    livro = models.CharField(max_length=500)  # ID do livro ou título
    visualizacoes = models.IntegerField(default=0)
    compartilhamentos_facebook = models.IntegerField(default=0)
    compartilhamentos_twitter = models.IntegerField(default=0)
    compartilhamentos_whatsapp = models.IntegerField(default=0)
    adicoes_estante = models.IntegerField(default=0)
    data = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('livro', 'data')
        indexes = [
            models.Index(fields=['livro', 'data']),
        ]

    @property
    def compartilhamentos_total(self):
        return (
                self.compartilhamentos_facebook +
                self.compartilhamentos_twitter +
                self.compartilhamentos_whatsapp
        )


class SearchAnalytics(models.Model):
    """Modelo para análise de buscas"""
    objects = models.Manager()
    termo_busca = models.CharField(max_length=200)
    tipo_busca = models.CharField(max_length=50)  # título, autor, etc.
    resultados_encontrados = models.IntegerField()
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(auto_now_add=True)
    foi_bem_sucedida = models.BooleanField(default=True)


class UserActivityLog(models.Model):
    """Modelo para log detalhado de atividades do usuário"""
    objects = models.Manager()
    objects = models.Manager()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=50)  # login, logout, adicionar_livro, etc.
    detalhes = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    secao_atual = models.CharField(max_length=50)


class ErrorLog(models.Model):
    """Modelo para registro de erros"""
    objects = models.Manager()
    timestamp = models.DateTimeField(auto_now_add=True)
    tipo_erro = models.CharField(max_length=100)
    mensagem = models.TextField()
    traceback = models.TextField(null=True)
    usuario = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    url = models.CharField(max_length=500)


class ReportExport(models.Model):
    """Modelo para controle de exportação de relatórios"""
    FORMATO_CHOICES = [
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
    ]
    objects = models.Manager()
    timestamp = models.DateTimeField(auto_now_add=True)
    tipo_relatorio = models.CharField(max_length=50)
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    arquivo = models.FileField(upload_to='reports/')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)


class AnalyticsSettings(models.Model):
    """Modelo para armazenar configurações do analytics"""
    objects = models.Manager()
    tracking_enabled = models.BooleanField(default=True)
    data_retention = models.IntegerField(default=90)  # dias
    daily_report = models.BooleanField(default=False)
    alert_threshold = models.IntegerField(default=100)
    notification_email = models.EmailField(blank=True, null=True)
    last_cleanup = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active_user_period = models.IntegerField(
        default=24,  # 24 horas
        help_text="Período em horas para considerar um usuário como ativo"
    )

    class Meta:
        verbose_name = 'Configuração do Analytics'
        verbose_name_plural = 'Configurações do Analytics'

    def __str__(self):
        return f'Configurações do Analytics (Atualizado em: {self.updated_at})'

    @classmethod
    def get_settings(cls):
        """Retorna as configurações atuais ou cria uma nova configuração padrão"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
