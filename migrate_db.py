#!/usr/bin/env python3
"""
Migração para adicionar coluna hidden_from_classroom
Execute este script no Railway via terminal ou acesse /admin/migrate_db no navegador
"""

from app import app, db
from sqlalchemy import text
import logging

def migrate_hidden_from_classroom():
    """Adiciona a coluna hidden_from_classroom à tabela incident"""
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # Para PostgreSQL
                try:
                    print("Tentando migração PostgreSQL...")
                    conn.execute(text("""
                        ALTER TABLE incident 
                        ADD COLUMN IF NOT EXISTS hidden_from_classroom BOOLEAN DEFAULT FALSE
                    """))
                    conn.commit()
                    print("✅ Migração PostgreSQL concluída!")
                    return True
                except Exception as e:
                    print(f"Migração PostgreSQL falhou: {e}")
                    
                # Para SQLite (fallback)
                try:
                    print("Tentando migração SQLite...")
                    conn.execute(text("""
                        ALTER TABLE incident 
                        ADD COLUMN hidden_from_classroom BOOLEAN DEFAULT FALSE
                    """))
                    conn.commit()
                    print("✅ Migração SQLite concluída!")
                    return True
                except Exception as e:
                    print(f"Migração SQLite falhou: {e}")
                    
                # Se tudo falhar, verificar se coluna já existe
                try:
                    result = conn.execute(text("SELECT hidden_from_classroom FROM incident LIMIT 1"))
                    print("✅ Coluna hidden_from_classroom já existe!")
                    return True
                except Exception as e:
                    print(f"❌ Coluna não existe e migração falhou: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Erro na migração: {e}")
            return False

if __name__ == "__main__":
    success = migrate_hidden_from_classroom()
    if success:
        print("🎉 Migração concluída com sucesso!")
    else:
        print("❌ Migração falhou!")