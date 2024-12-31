# Sistema de Backup do Banco de Dados

## Estrutura de Diretórios

```
backups/
└── database/
    ├── current/     # Banco atual e último backup
    └── archive/     # Backups históricos
```

## Organização

### Diretório `current/`
- Contém o banco de dados atual (`db.sqlite3`)
- Mantém o último backup bem-sucedido
- Linkado simbolicamente com a raiz do projeto

### Diretório `archive/`
- Armazena backups históricos
- Nomenclatura: `db_backup_YYYYMMDD_HHMMSS.sqlite3`
- Mantido para referência e recuperação

## Procedimentos

### Novo Backup
1. Gerar backup usando `backup_db.py`
2. Arquivo gerado vai para `current/`
3. Backup anterior move para `archive/`

### Restauração
1. Copiar arquivo de backup desejado de `archive/` para `current/`
2. Renomear para `db.sqlite3`
3. Atualizar link simbólico se necessário

## Manutenção

- Limpar backups mais antigos que 30 dias do `archive/`
- Manter pelo menos os últimos 5 backups
- Verificar integridade dos backups periodicamente

## Notas Importantes

- Não remover o link simbólico na raiz
- Manter permissões corretas nos diretórios
- Sempre usar os scripts de backup fornecidos