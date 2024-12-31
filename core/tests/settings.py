# core/tests/settings.py
from django.test.runner import DiscoverRunner

class NoMigrationTestRunner(DiscoverRunner):
    """Classe para executar testes sem migrações"""
    def setup_databases(self, **kwargs):
        # Desabilita migrações e usa banco de dados em memória
        from django.db import connection
        connection.creation.create_test_db()
        return super().setup_databases(**kwargs)

# Configure o banco de dados para testes
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
