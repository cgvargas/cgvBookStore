import os
import sys
import shutil
from datetime import datetime
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')
django.setup()


def create_backup():
    """
    Creates a backup of the migrations directory
    """
    try:
        print("🔄 Iniciando processo de backup...")

        # Create backup directory if it doesn't exist
        backup_dir = 'backups/migrations'
        os.makedirs(backup_dir, exist_ok=True)

        # Generate timestamp for backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Source migrations directory
        migrations_dir = 'core/migrations'

        if not os.path.exists(migrations_dir):
            print(f"❌ Diretório de migrações não encontrado: {migrations_dir}")
            return False

        # Create backup directory with timestamp
        backup_path = os.path.join(backup_dir, f'migrations_backup_{timestamp}')

        # Copy the entire migrations directory
        shutil.copytree(migrations_dir, backup_path, dirs_exist_ok=True)

        # Verify the backup
        if os.path.exists(backup_path):
            print(f"✅ Backup criado com sucesso em: {backup_path}")

            # List backed up files
            print("\nArquivos incluídos no backup:")
            for file in os.listdir(backup_path):
                if file.endswith('.py'):
                    print(f"  - {file}")

            return True
        else:
            print("❌ Falha na verificação do backup")
            return False

    except Exception as e:
        print(f"❌ Erro ao criar backup:\n{str(e)}")
        return False


if __name__ == "__main__":
    try:
        if create_backup():
            print("\n✅ Processo de backup concluído com sucesso")
        else:
            print("\n❌ Processo interrompido devido a erro no backup")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico durante o backup:\n{str(e)}")
        sys.exit(1)