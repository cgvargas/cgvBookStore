# Setup - CGV BookStore

## Ambiente de Desenvolvimento
- Python 3.x
- Django 4.x
- Ambiente virtual (.venv)

## Configuração Inicial
1. Clonar repositório
2. Criar e ativar ambiente virtual
3. Instalar dependências
4. Executar migrações
5. Configurar variáveis de ambiente
6. Popular cache inicial de livros

## Comandos Importantes
```bash
# Ativar ambiente virtual
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar migrações
python manage.py migrate

# Popular cache de livros
python manage.py populate_book_cache

# Rodar servidor
python manage.py runserver
```