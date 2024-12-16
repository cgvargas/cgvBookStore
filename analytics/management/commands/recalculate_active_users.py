# analytics/management/commands/recalculate_active_users.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from analytics.models import SiteAnalytics, PageView
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Recalcula usuários ativos baseado nos logs de PageView'

    def handle(self, *args, **options):
        # Obtém a data atual
        today = timezone.now().date()

        # Recalcula para os últimos 7 dias
        for i in range(7):
            date = today - timedelta(days=i)

            # Conta usuários únicos que fizeram requisições neste dia
            active_users = PageView.objects.filter(
                timestamp__date=date,
                usuario__isnull=False
            ).values('usuario').distinct().count()

            # Atualiza ou cria registro de analytics
            analytics, _ = SiteAnalytics.objects.get_or_create(data=date)
            analytics.usuarios_ativos = active_users
            analytics.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Data: {date} - Usuários ativos: {active_users}'
                )
            )
