import os
import shutil
from datetime import datetime
import pathlib


def create_backup():
    """
    Cria um backup do banco de dados SQLite usando cópia direta
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_backup = f'db_backup_{timestamp}.sqlite3'

    try:
        # Verificar se o banco original existe
        if not os.path.exists('db.sqlite3'):
            print('❌ Arquivo db.sqlite3 não encontrado!')
            return False

        # Criar cópia do banco
        print('📂 Criando cópia do banco de dados...')
        shutil.copy2('db.sqlite3', db_backup)

        # Verificar se o backup foi criado corretamente
        if os.path.exists(db_backup):
            original_size = os.path.getsize('db.sqlite3')
            backup_size = os.path.getsize(db_backup)

            if original_size == backup_size:
                print(f'✅ Backup criado com sucesso: {db_backup}')
                print(f'📊 Tamanho do arquivo: {backup_size:,} bytes')
                return True
            else:
                print('❌ Erro: Tamanho do backup difere do original!')
                return False

    except Exception as e:
        print(f'❌ Erro durante o backup: {str(e)}')
        return False


def list_recent_backups():
    """
    Lista os backups mais recentes
    """
    backups = [f for f in os.listdir('.') if f.startswith('db_backup_') and f.endswith('.sqlite3')]
    if backups:
        backups.sort(reverse=True)
        print('\n📋 Backups encontrados:')
        for backup in backups[:3]:  # Mostra os 3 mais recentes
            size = os.path.getsize(backup)
            print(f'  - {backup} ({size:,} bytes)')


def main():
    print('🔄 Iniciando processo de backup...\n')

    if create_backup():
        list_recent_backups()
        print('\n✅ Processo de backup concluído com sucesso!')
        print('\n🔄 Próximos passos:')
        print('1. Execute: python manage.py showmigrations core')
        print('2. Execute: python manage.py squashmigrations core 0001')
        print('3. Verifique o arquivo de migração gerado')
    else:
        print('\n❌ Processo de backup falhou, verifique os erros acima')


if __name__ == '__main__':
    main()