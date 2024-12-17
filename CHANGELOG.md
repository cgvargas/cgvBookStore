# Changelog - Reestruturação CGV BookStore

## [2024-12-17] - Correção Sistema de Recomendações
### Corrigido
- Sistema de cache de livros implementado e corrigido
- Problema de cache vazio nas recomendações resolvido
- Questões de importação circular nos modelos

### Adicionado
- Novo sistema de cache (NewLivroCache)
- Migração de dados para popular cache
- Comando de management para população do cache
- Melhor tratamento de erros no sistema de cache

### Modificado
- Serviço de recomendações atualizado para usar novo sistema de cache
- Otimização na geração de recomendações
- Estrutura de modelos para melhor performance

## [2024-12-16] - Início da Reestruturação
### Adicionado
- Nova estrutura de diretórios core
  - domain/
  - infrastructure/
  - application/
  - presentation/
- Sistema de recomendações
  - Implementado domain layer
  - Implementado infrastructure layer
  - Adicionadas novas URLs

### Em Progresso
- Admin interface
- Migração do frontend
- Atualização da documentação