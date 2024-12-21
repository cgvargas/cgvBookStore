import os
from pathlib import Path
from typing import List, Tuple
from colorama import init, Fore, Style

# Inicializa o colorama para saída colorida no terminal
init()


class ImportChecker:
    def __init__(self, base_path: str = 'core'):
        self.base_path = Path(base_path)
        # Padrões que queremos identificar como potencialmente problemáticos
        self.old_patterns = [
            'from core.models',  # imports antigos do models.py
            'from ..models',  # imports relativos do models antigo
            'from .models',  # imports locais do models
            'import models',  # imports diretos do models
            '.objects.get',  # possíveis acessos diretos ao banco
            '.objects.filter',  # possíveis acessos diretos ao banco
            'from django.db import models'  # possíveis models antigos
        ]

        # Exceções - arquivos ou diretórios que podemos ignorar
        self.ignored_paths = {
            '__pycache__',
            'migrations',
            'tests',
            'validation'
        }

    def should_check_file(self, file_path: Path) -> bool:
        """Verifica se o arquivo deve ser analisado"""
        return (
                file_path.suffix == '.py' and
                not any(ignored in file_path.parts for ignored in self.ignored_paths)
        )

    def check_file(self, file_path: Path) -> List[str]:
        """Analisa um arquivo em busca de padrões problemáticos"""
        issues = []
        try:
            content = file_path.read_text(encoding='utf-8')
            for line_number, line in enumerate(content.splitlines(), 1):
                for pattern in self.old_patterns:
                    if pattern in line:
                        issues.append({
                            'file': file_path,
                            'line': line_number,
                            'pattern': pattern,
                            'content': line.strip()
                        })
        except Exception as e:
            issues.append({
                'file': file_path,
                'line': 0,
                'pattern': 'ERROR',
                'content': f"Erro ao ler arquivo: {str(e)}"
            })
        return issues

    def validate_imports(self) -> Tuple[List[dict], List[Path]]:
        """Executa a validação em todos os arquivos Python do projeto"""
        issues = []
        checked_files = []

        for python_file in self.base_path.rglob("*"):
            if self.should_check_file(python_file):
                checked_files.append(python_file)
                file_issues = self.check_file(python_file)
                issues.extend(file_issues)

        return issues, checked_files


def print_colored(text: str, color: str = Fore.WHITE, bold: bool = False):
    """Imprime texto colorido no terminal"""
    style = Style.BRIGHT if bold else ""
    print(f"{style}{color}{text}{Style.RESET_ALL}")


def run_import_check(base_path: str = 'core'):
    """Executa a verificação e exibe os resultados formatados"""
    print_colored("\n=== Iniciando verificação de imports ===\n", Fore.CYAN, True)

    checker = ImportChecker(base_path)
    issues, checked_files = checker.validate_imports()

    print_colored(f"Arquivos verificados: {len(checked_files)}", Fore.CYAN)

    if issues:
        print_colored("\nProblemas encontrados:", Fore.YELLOW, True)
        current_file = None

        # Agrupa problemas por arquivo para melhor visualização
        for issue in sorted(issues, key=lambda x: (x['file'], x['line'])):
            if current_file != issue['file']:
                current_file = issue['file']
                print_colored(f"\nArquivo: {current_file}", Fore.GREEN, True)

            print_colored(
                f"  Linha {issue['line']}: {issue['pattern']}",
                Fore.YELLOW
            )
            print_colored(f"    {issue['content']}", Fore.WHITE)
    else:
        print_colored("\nNenhum problema de importação encontrado!", Fore.GREEN, True)

    print_colored("\n=== Verificação concluída ===\n", Fore.CYAN, True)
    return len(issues) == 0


if __name__ == "__main__":
    import sys

    # Permite especificar um caminho base diferente via linha de comando
    base_path = sys.argv[1] if len(sys.argv) > 1 else 'core'
    success = run_import_check(base_path)

    # Retorna código de erro se encontrar problemas (útil para CI/CD)
    sys.exit(0 if success else 1)