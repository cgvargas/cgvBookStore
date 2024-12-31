import os
import subprocess
from datetime import datetime
import shutil


def create_sqlite_backup():
    """
    Cria um backup do banco de dados SQLite usando cópia direta e dump
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_backup = f'db_backup_{timestamp}.sqlite3'
    sql_backup = f'db_dump_{timestamp}.sql'

    try:
        # 1. Cópia direta do arquivo do banco
        print('📂 Criando cópia do banco de dados...')
        shutil.copy2('db.sqlite3', db_backup)
        print(f'✅ Backup do banco criado: {db_backup}')

        # 2. Criar dump SQL como backup adicional
        print('\n📝 Gerando dump SQL...')
        result = subprocess.run(
            ['sqlite3', 'db.sqlite3', '.dump'],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            with open(sql_backup, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print(f'✅ Dump SQL criado: {sql_backup}')
            return True
        else:
            print('❌ Erro ao criar dump SQL:')
            print(result.stderr)
            return False

    except Exception as e:
        print(f'❌ Erro durante o backup: {str(e)}')
        return False


def verify_backups():
    """
    Verifica se os backups foram criados corretamente
    """
    backups = [f for f in os.listdir('.') if f.startswith(('db_backup_', 'db_dump_'))]
    if not backups:
        return False

    latest_backup = max(f for f in backups if f.endswith('.sqlite3'))
    latest_dump = max(f for f in backups if f.endswith('.sql'))

    backup_size = os.path.getsize(latest_backup)
    dump_size = os.path.getsize(latest_dump)

    if backup_size > 0 and dump_size > 0:
        return True
    return False


def main():
    print('🔄 Iniciando processo de backup...\n')

    if create_sqlite_backup() and verify_backups():
        print('\n✅ Processo de backup concluído com sucesso!')
        print('\n🔄 Próximos passos:')
        print('1. Verifique os arquivos de backup gerados')
        print('2. Execute: python manage.py squashmigrations core 0001')
        print('3. Verifique o arquivo de migração gerado')
        print('4. Teste a migração em um ambiente de desenvolvimento')
    else:
        print('\n❌ Processo de backup falhou, verifique os erros acima')


if __name__ == '__main__':
    main()