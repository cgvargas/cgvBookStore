# CHANGELOG.md

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