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

### Modificado
- Renomeadas classes para inglês mantendo compatibilidade com banco
- Reorganização dos models seguindo Clean Architecture
- Models movidos para seus respectivos domínios

## [2024-12-19] - Reorganização CSS e Ajustes no Sistema
[manter o conteúdo anterior...]