# 🚀 INSTRUÇÕES PARA CORREÇÃO NO RAILWAY

## OPÇÃO 1: Script Automático (Recomendado)
Execute no terminal do Railway:
```bash
python railway_ultimate_fix.py
```

## OPÇÃO 2: Via Navegador
Acesse: `https://sua-url.railway.app/admin/migrate_db`

## OPÇÃO 3: Manual (Se as opções acima falharem)

### 1. Verificar variáveis de ambiente
```bash
echo $DATABASE_URL
```

### 2. Executar comandos SQL manualmente
```sql
-- Adicionar colunas faltantes na tabela incident
ALTER TABLE incident ADD COLUMN IF NOT EXISTS hidden_from_classroom BOOLEAN DEFAULT FALSE;
ALTER TABLE incident ADD COLUMN IF NOT EXISTS is_resolved BOOLEAN DEFAULT FALSE;
ALTER TABLE incident ADD COLUMN IF NOT EXISTS admin_response TEXT;
ALTER TABLE incident ADD COLUMN IF NOT EXISTS response_date TIMESTAMP;

-- Adicionar colunas faltantes na tabela classroom
ALTER TABLE classroom ADD COLUMN IF NOT EXISTS image_data BYTEA;
ALTER TABLE classroom ADD COLUMN IF NOT EXISTS excel_data BYTEA;
ALTER TABLE classroom ADD COLUMN IF NOT EXISTS image_mimetype VARCHAR(100);
ALTER TABLE classroom ADD COLUMN IF NOT EXISTS excel_mimetype VARCHAR(100);
ALTER TABLE classroom ADD COLUMN IF NOT EXISTS admin_password VARCHAR(255) DEFAULT '';

-- Adicionar colunas faltantes na tabela schedule
ALTER TABLE schedule ADD COLUMN IF NOT EXISTS start_date DATE;
ALTER TABLE schedule ADD COLUMN IF NOT EXISTS end_date DATE;
ALTER TABLE schedule ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- Limpar dados inconsistentes
UPDATE incident SET hidden_from_classroom = FALSE WHERE hidden_from_classroom IS NULL;
UPDATE incident SET is_resolved = FALSE WHERE is_resolved IS NULL;
UPDATE incident SET is_active = TRUE WHERE is_active IS NULL;
UPDATE classroom SET admin_password = '' WHERE admin_password IS NULL;
UPDATE schedule SET is_active = TRUE WHERE is_active IS NULL;
```

### 3. Verificar se funcionou
Teste estas URLs:
- `/` - Homepage
- `/dashboard` - Dashboard
- `/incidents_management` - Gestão de ocorrências
- `/classroom/1` - Detalhes de sala

## ✅ Resultado Esperado
- ✅ Todas as páginas carregando sem erro 500
- ✅ Gestão de ocorrências funcionando
- ✅ Sistema totalmente operacional
- ✅ Compatibilidade 100% com PostgreSQL

## 🆘 Se ainda não funcionar
1. Verifique os logs do Railway para erros específicos
2. Confirme que todas as dependências estão instaladas
3. Verifique se o PostgreSQL está acessível
4. Entre em contato incluindo os logs de erro