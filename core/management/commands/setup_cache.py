# core/management/commands/setup_cache.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.core.cache.backends.db import DatabaseCache
from django.db import connection

class Command(BaseCommand):
    help = 'Configura as tabelas de cache necessárias'

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # Verifica se a tabela existe
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='cache_table'
                """)
                if not cursor.fetchone():
                    # Cria a tabela de cache
                    DatabaseCache.create_table()
                    self.stdout.write(
                        self.style.SUCCESS('Tabela de cache criada com sucesso')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS('Tabela de cache já existe')
                    )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro ao criar tabela de cache: {str(e)}')
            )