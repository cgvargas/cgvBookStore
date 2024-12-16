# analytics/management/commands/setup_analytics.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from analytics.models import (
    SiteAnalytics, PageView, BookAnalytics,
    SearchAnalytics, UserActivityLog, ErrorLog,
    ReportExport
)


class Command(BaseCommand):
    help = 'Configura grupos e permissões necessárias para o sistema de analytics'

    def handle(self, *args, **kwargs):
        self.stdout.write('Configurando grupos e permissões do analytics...')

        # Cria ou obtém o grupo Analytics_Admin
        analytics_group, created = Group.objects.get_or_create(name='Analytics_Admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo Analytics_Admin criado'))
        else:
            self.stdout.write('Grupo Analytics_Admin já existe')

        # Lista de modelos que precisam de permissões
        models = [
            SiteAnalytics,
            PageView,
            BookAnalytics,
            SearchAnalytics,
            UserActivityLog,
            ErrorLog,
            ReportExport
        ]

        # Adiciona permissões para cada modelo
        for model in models:
            ct = ContentType.objects.get_for_model(model)
            permissions = Permission.objects.filter(content_type=ct)

            for perm in permissions:
                analytics_group.permissions.add(perm)
                self.stdout.write(f'Adicionada permissão: {perm.codename}')

        self.stdout.write(self.style.SUCCESS(
            'Configuração do analytics concluída com sucesso!'
        ))
        self.stdout.write(
            'Para adicionar um usuário ao grupo, use: '
            'python manage.py shell\n'
            'from django.contrib.auth.models import User, Group\n'
            'user = User.objects.get(username="seu_usuario")\n'
            'group = Group.objects.get(name="Analytics_Admin")\n'
            'user.groups.add(group)'
        )