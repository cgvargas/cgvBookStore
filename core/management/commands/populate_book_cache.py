# core/management/commands/populate_book_cache.py
from django.core.management.base import BaseCommand
from core.infrastructure.persistence.django.models import NewLivroCache

class Command(BaseCommand):
    help = 'Popula o cache de livros com dados da estante'

    def handle(self, *args, **options):
        self.stdout.write('Populando cache de livros...')
        NewLivroCache.populate_initial_cache()
        self.stdout.write(self.style.SUCCESS('Cache populado com sucesso!'))