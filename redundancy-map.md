# Mapeamento de Redundâncias - CGVBookStore

## Estrutura de Análise
Para cada arquivo/diretório, usaremos a seguinte classificação:
- 🔴 Remover: Arquivo completamente redundante que pode ser removido
- 🟡 Migrar: Contém código que precisa ser migrado para nova estrutura
- 🟢 Manter: Arquivo atual/necessário
- ❓ Verificar: Necessita análise adicional

## Core Package

### Arquivos Antigos vs Nova Estrutura

#### Models e Persistência
- 🟡 `core/models/` 
  - Substituído por: `core/infrastructure/persistence/django/models/`
  - Ação: Migrar qualquer lógica de domínio restante para as novas entidades
  - Prioridade: Alta

#### Casos de Uso
- 🟡 `core/usecases/` (estrutura antiga)
  - Substituído por: `core/application/use_cases/`
  - Ação: Verificar implementações e migrar lógica faltante
  - Prioridade: Alta

#### Interfaces
- 🟡 `core/interfaces/` (se existir)
  - Substituído por: `core/domain/interfaces/`
  - Ação: Alinhar com princípios da Clean Architecture
  - Prioridade: Média

#### Serviços
- 🟡 `core/services/` (estrutura antiga)
  - Substituído por: `core/domain/services/`
  - Ação: Migrar regras de negócio e validações
  - Prioridade: Alta

### Sistemas Específicos

#### Sistema de Recomendações
- ❓ `core/recommendations/`
  - Verificar se já existe implementação na nova estrutura
  - Avaliar necessidade de refatoração
  - Prioridade: Média

#### Cache de Livros
- 🟡 `core/cache/`
  - Relacionado a: `NewLivroCache` nas migrações
  - Ação: Alinhar com novas implementações
  - Prioridade: Média

## Próximos Passos

1. Validação Inicial
   - Confirmar estrutura atual dos diretórios
   - Identificar dependências entre componentes
   - Mapear testes existentes

2. Processo de Migração
   - Começar pelos componentes de alta prioridade
   - Manter testes funcionando durante a migração
   - Documentar mudanças no CHANGELOG.md

3. Limpeza
   - Remover código comentado
   - Eliminar importações não utilizadas
   - Atualizar documentação conforme necessário

## Observações
- Manter backup antes de qualquer remoção
- Atualizar testes conforme código é migrado
- Documentar decisões de arquitetura
- Verificar impacto em outras partes do sistema

## Status do Mapeamento
- [ ] Validação inicial completa
- [ ] Dependências mapeadas
- [ ] Plano de migração aprovado
- [ ] Testes adequados identificados