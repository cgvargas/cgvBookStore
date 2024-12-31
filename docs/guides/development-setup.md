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

## Nova Estrutura Administrativa
```
core/presentation/admin/
    ├── __init__.py            # Configurações gerais
    ├── book_admin.py          # Livros e Cache
    ├── user_admin.py          # Usuários
    ├── media_admin.py         # URLs e Vídeos
    └── interaction_admin.py   # Contatos e Interações
```

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

## Estrutura do Projeto
O projeto segue uma arquitetura limpa (clean architecture) com as seguintes camadas:

1. Domain - Regras de negócio e entidades
2. Application - Casos de uso e serviços
3. Infrastructure - Implementações técnicas
4. Presentation - Interface com usuário e admin

## Configurações Adicionais
1. Configurar variáveis no arquivo .env
2. Verificar permissões de diretórios media/ e static/
3. Configurar banco de dados se necessário
4. Executar collectstatic para arquivos estáticos

## Nova Estrutura de Assets
```bash
static/
    ├── css/
    │   ├── book_detail.css
    │   ├── main.css
    │   └── [outros arquivos CSS]
    └── js/
        ├── auto-logout-v2.js
        ├── book_detail.js
        └── [outros arquivos JS]
```

## Nova Estrutura de Repositories
```bash
core/infrastructure/persistence/django/repositories/
    ├── base.py                 # Repository base
    ├── books/                  # Repositories de livros
    │   ├── book_repository.py
    │   ├── book_cache_repository.py
    │   └── bookshelf_repository.py
    ├── users/                  # Repositories de usuários
    │   ├── user_repository.py
    │   └── activity_history_repository.py
    ├── media/                  # Repositories de mídia
    │   ├── external_url_repository.py
    │   └── youtube_video_repository.py
    ├── contact/                # Repository de contatos
    │   └── contact_repository.py
    └── preferences/            # Repository de preferências
        └── preferences_repository.py
```
