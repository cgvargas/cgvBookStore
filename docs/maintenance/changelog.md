# CHANGELOG.md

## [2024-12-31] - Correções na Estrutura DDD e Contact Form
### Modificado
- Refatoração do módulo de contato para seguir corretamente a arquitetura DDD
  - Movido modelo Contact para infrastructure/persistence/django/models/contact.py
  - Atualizado ContactRepository para usar corretamente o BaseRepository
  - Separação clara entre entidade de domínio e modelo de persistência
- Correções na estrutura de logging para remover filtros desnecessários
- Atualização do formulário de contato para funcionar com a nova estrutura

## [2024-12-30] - Reorganização de Forms
### Adicionado
- Nova estrutura de forms em core/presentation/forms/
  - books/: Formulários relacionados a livros
  - users/: Formulários de usuários
  - contact/: Formulários de contato
- Importação `BookShelf as EstanteLivro` para manter compatibilidade

### Modificado
- Migração do LivroManualForm para nova estrutura em core/presentation/forms/books/
- Atualização das importações para usar o novo caminho
- Mantida compatibilidade com nome em português (EstanteLivro)

## [2024-12-21] - Implementação do Repository Pattern
### Adicionado
- Base Repository com funcionalidades comuns
- Repositories específicos:
  - Books: BookRepository, BookCacheRepository, BookShelfRepository
  - Users: UserRepository, ActivityHistoryRepository
  - Media: ExternalURLRepository, YouTubeVideoRepository
  - Contact: ContactRepository
  - Preferences: PreferencesRepository
- Módulo de validação com import_checker.py
- Views atualizadas para usar repositories

## [2024-12-21] - Implementação do Repository Pattern
### Adicionado
- Base Repository com funcionalidades comuns
- Repositories específicos:
  - Books: BookRepository, BookCacheRepository, BookShelfRepository
  - Users: UserRepository, ActivityHistoryRepository
  - Media: ExternalURLRepository, YouTubeVideoRepository
  - Contact: ContactRepository
  - Preferences: PreferencesRepository
- Módulo de validação com import_checker.py
- Views atualizadas para usar repositories

### Modificado
- Views principais refatoradas para usar repositories:
  - profile_views.py
  - book_actions.py
  - book_views.py
  - general_views.py
- Estrutura de repositories seguindo Clean Architecture
- Atualização dos módulos de domínio

## [2024-12-20] - Reestruturação do Domain Layer
### Adicionado
- Novos módulos de domínio em core/domain/
  - books: Book, BookCache, BookShelf
  - users: User, ActivityHistory
  - media: ExternalURL, YouTubeVideo
  - contact: Contact
- Implementação de __init__.py para todos os módulos de domínio
- Métodos utilitários adicionados às entidades

### Modificadoz
- Renomeadas classes para inglês mantendo compatibilidade com banco
- Reorganização dos models seguindo Clean Architecture
- Models movidos para seus respectivos domínios

## [2024-12-19] - Reorganização CSS e Ajustes no Sistema
### Adicionado
- Novo arquivo auto-logout-v2.js com melhorias no sistema de logout automático
- Novo CSS consolidado para detalhes de livros

### Modificado
- Mantida estrutura de models com prefixo "New" para estabilidade
- Reorganização completa da estrutura de arquivos CSS
- Atualizações em views e templates relacionados a livros
- Melhorias no sistema de analytics e middleware
- Ajustes nos templates base e detalhes de livros

### Removido
- Estrutura antiga de CSS (componentes, utilitários, layout)
- Versão antiga do auto-logout.js

## [2024-12-17] - Reestruturação Interface Administrativa
### Adicionado
- Nova estrutura administrativa em core/presentation/admin/
 - book_admin.py para gestão de livros e cache
 - user_admin.py para gestão de usuários
 - media_admin.py para gestão de URLs e vídeos
 - interaction_admin.py para gestão de contatos e interações
- Funcionalidades visuais melhoradas no admin
 - Visualizações de imagens
 - Indicadores de status
 - Links clicáveis
 - Melhor organização de campos

### Modificado
- Reorganização do arquivo core/admin.py
- Migração das classes Admin para estrutura modular
- Melhoria na apresentação dos dados administrativos

### Corrigido
- Sistema de cache de livros implementado e corrigido
- Problema de cache vazio nas recomendações resolvido
- Questões de importação circular nos modelos 