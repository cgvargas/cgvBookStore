# analytics/tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import timedelta
from .models import SiteAnalytics, PageView, BookAnalytics, UserActivityLog
from .utils import AnalyticsProcessor

User = get_user_model()


class AnalyticsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )

        # Cria dados de analytics para teste
        self.analytics = SiteAnalytics.objects.create(
            data=timezone.now().date(),
            visitas_total=100,
            visitas_autenticadas=60,
            visitas_anonimas=40,
            usuarios_ativos=50
        )

        self.page_view = PageView.objects.create(
            url='/test-page/',
            usuario=self.user,
            sessao_id='test-session',
            dispositivo='desktop',
            navegador='chrome',
            tempo_na_pagina=timedelta(minutes=5)
        )

    def test_site_analytics_creation(self):
        """Testa a criação de registro de analytics do site"""
        self.assertEqual(self.analytics.visitas_total, 100)
        self.assertEqual(self.analytics.visitas_autenticadas, 60)
        self.assertEqual(self.analytics.visitas_anonimas, 40)
        self.assertEqual(self.analytics.usuarios_ativos, 50)

    def test_page_view_creation(self):
        """Testa a criação de registro de visualização de página"""
        self.assertEqual(self.page_view.url, '/test-page/')
        self.assertEqual(self.page_view.usuario, self.user)
        self.assertEqual(self.page_view.dispositivo, 'desktop')
        self.assertEqual(self.page_view.navegador, 'chrome')


class AnalyticsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Cria superusuário
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='test@example.com',
            password='testpass123'
        )

        # Cria grupo Analytics_Admin
        self.analytics_group = Group.objects.create(name='Analytics_Admin')
        self.admin_user.groups.add(self.analytics_group)

        # Cria usuário normal para testes de permissão
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normal123'
        )

        # Cria alguns dados de teste
        self.create_test_data()

    def create_test_data(self):
        """Cria dados de teste para analytics"""
        today = timezone.now().date()

        # Cria analytics para os últimos 7 dias
        for i in range(7):
            date = today - timedelta(days=i)
            SiteAnalytics.objects.create(
                data=date,
                visitas_total=100 + i,
                visitas_autenticadas=60 + i,
                visitas_anonimas=40,
                usuarios_ativos=50
            )

    def test_dashboard_access_admin(self):
        """Testa acesso ao dashboard por usuário admin"""
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/dashboard.html')

    def test_dashboard_access_denied_normal_user(self):
        """Testa negação de acesso ao dashboard por usuário normal"""
        self.client.login(username='normaluser', password='normal123')
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirecionamento

    def test_get_analytics_data(self):
        """Testa API de dados do analytics"""
        self.client.login(username='testadmin', password='testpass123')
        response = self.client.get(reverse('analytics:get_data'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('trend_data' in response.json())

    def test_export_excel_report(self):
        """Testa exportação de relatório Excel"""
        self.client.login(username='testadmin', password='testpass123')

        # Cria dados de teste
        start_date = timezone.now().date() - timedelta(days=7)
        end_date = timezone.now().date()

        # Garante que existem dados para o período
        SiteAnalytics.objects.create(
            data=start_date,
            visitas_total=100,
            visitas_autenticadas=60,
            visitas_anonimas=40,
            usuarios_ativos=50
        )

        response = self.client.get(
            reverse('analytics:export_excel'),
            {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )


class AnalyticsProcessorTests(TestCase):
    def setUp(self):
        self.today = timezone.now().date()
        self.create_test_data()

    def create_test_data(self):
        """Cria dados de teste para o processador"""
        for i in range(7):
            date = self.today - timedelta(days=i)
            SiteAnalytics.objects.create(
                data=date,
                visitas_total=100 + i,
                visitas_autenticadas=60 + i,
                visitas_anonimas=40,
                usuarios_ativos=50
            )

    def test_process_trend_data(self):
        """Testa processamento de dados de tendência"""
        start_date = self.today - timedelta(days=6)
        end_date = self.today

        queryset = SiteAnalytics.objects.filter(
            data__range=[start_date, end_date]
        )

        trend_data = AnalyticsProcessor.process_trend_data(
            queryset, start_date, end_date
        )

        self.assertEqual(len(trend_data), 7)
        self.assertTrue(all(
            'total' in data and
            'authenticated' in data and
            'anonymous' in data
            for data in trend_data
        ))

    def test_process_devices_data(self):
        """Testa processamento de dados de dispositivos"""
        PageView.objects.create(
            url='/test/',
            dispositivo='desktop',
            navegador='chrome',
            sessao_id='test'
        )
        PageView.objects.create(
            url='/test/',
            dispositivo='mobile',
            navegador='safari',
            sessao_id='test2'
        )

        devices_data = AnalyticsProcessor.process_devices_data(
            PageView.objects.all()
        )

        self.assertTrue('desktop' in devices_data)
        self.assertTrue('mobile' in devices_data)
