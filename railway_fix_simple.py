#!/usr/bin/env python3
"""
SOLUÇÃO DEFINITIVA PARA RAILWAY
Execute este comando no terminal do Railway:

python railway_fix_simple.py

OU acesse no navegador: https://sua-url.railway.app/admin/migrate_db

Este script corrige o erro da coluna hidden_from_classroom
"""

import os
import sys

def fix_railway():
    # Configurar as variáveis de ambiente necessárias  
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        print("🔧 INICIANDO CORREÇÃO RAILWAY...")
        print("🔧 Corrigindo banco PostgreSQL no Railway...")
        
        with app.app_context():
            with db.engine.connect() as conn:
                print("✅ Conectado ao banco PostgreSQL")
                
                # Verificar se a coluna já existe
                try:
                    result = conn.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='incident' 
                        AND column_name='hidden_from_classroom'
                    """))
                    column_exists = result.fetchone() is not None
                    print(f"📊 Coluna hidden_from_classroom existe: {column_exists}")
                except Exception as e:
                    print(f"⚠️  Erro ao verificar coluna: {e}")
                    column_exists = False
                
                # Adicionar coluna se não existir
                if not column_exists:
                    try:
                        conn.execute(text("""
                            ALTER TABLE incident 
                            ADD COLUMN hidden_from_classroom BOOLEAN DEFAULT FALSE
                        """))
                        conn.commit()
                        print("✅ Coluna hidden_from_classroom adicionada!")
                    except Exception as e:
                        print(f"❌ Erro ao adicionar coluna: {e}")
                        return False
                else:
                    print("✅ Coluna hidden_from_classroom já existe!")
                
                # Garantir que valores nulos sejam FALSE
                try:
                    result = conn.execute(text("""
                        UPDATE incident 
                        SET hidden_from_classroom = FALSE 
                        WHERE hidden_from_classroom IS NULL
                    """))
                    conn.commit()
                    updated_rows = result.rowcount if hasattr(result, 'rowcount') else 0
                    print(f"✅ {updated_rows} registros com valores nulos corrigidos!")
                except Exception as e:
                    print(f"⚠️  Info update: {e}")
                
                # Teste final
                try:
                    result = conn.execute(text("""
                        SELECT COUNT(*) FROM incident 
                        WHERE hidden_from_classroom IS NOT NULL
                    """))
                    count = result.scalar()
                    print(f"✅ Teste final: {count} registros com hidden_from_classroom válido")
                    
                    # Teste da query que estava falhando
                    result = conn.execute(text("""
                        SELECT id, hidden_from_classroom 
                        FROM incident 
                        WHERE is_active = true 
                        LIMIT 1
                    """))
                    test_row = result.fetchone()
                    if test_row:
                        print("✅ Query de teste funcionando corretamente!")
                    else:
                        print("✅ Sem registros, mas estrutura está correta!")
                        
                except Exception as e:
                    print(f"❌ Erro no teste final: {e}")
                    return False
                
        print("\n🎉🎉🎉 SUCESSO TOTAL! Problema corrigido! 🎉🎉🎉")
        print("✅ A gestão de ocorrências agora deve funcionar!")
        print("✅ Acesse: /incidents_management")
        print("✅ Sistema totalmente operacional!")
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print("\n🔧 ALTERNATIVAS:")
        print("1. Acesse no navegador: https://sua-url.railway.app/admin/migrate_db")
        print("2. Execute: python fix_railway.py")
        print("3. Execute: python migrate_db.py")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("   CORREÇÃO RAILWAY - HIDDEN_FROM_CLASSROOM")
    print("=" * 50)
    success = fix_railway()
    print("=" * 50)
    if success:
        print("STATUS: ✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
    else:
        print("STATUS: ❌ MIGRAÇÃO FALHOU - USE ALTERNATIVAS")
    print("=" * 50)