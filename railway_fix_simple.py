#!/usr/bin/env python3
"""
SOLUÇÃO DEFINITIVA PARA RAILWAY
Execute este comando no terminal do Railway:

python railway_fix_simple.py

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
        
        print("🔧 Corrigindo banco PostgreSQL no Railway...")
        
        with app.app_context():
            with db.engine.connect() as conn:
                print("✅ Conectado ao banco")
                
                # Comando direto para PostgreSQL
                try:
                    conn.execute(text("""
                        ALTER TABLE incident 
                        ADD COLUMN hidden_from_classroom BOOLEAN DEFAULT FALSE
                    """))
                    conn.commit()
                    print("✅ Coluna hidden_from_classroom adicionada!")
                except Exception as e:
                    if 'already exists' in str(e) or 'duplicate' in str(e):
                        print("✅ Coluna hidden_from_classroom já existe!")
                    else:
                        print(f"Info: {e}")
                
                # Garantir que valores nulos sejam corrigidos
                try:
                    conn.execute(text("""
                        UPDATE incident 
                        SET hidden_from_classroom = FALSE 
                        WHERE hidden_from_classroom IS NULL
                    """))
                    conn.commit()
                    print("✅ Valores nulos corrigidos!")
                except Exception as e:
                    print(f"Info update: {e}")
                
                # Testar se tudo funciona
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM incident 
                    WHERE hidden_from_classroom IS NOT NULL
                """))
                count = result.scalar()
                print(f"✅ Teste: {count} registros com hidden_from_classroom válido")
                
        print("\n🎉 SUCESSO! Problema corrigido!")
        print("Agora acesse: /incidents_management")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        print("\nAlternativa: Acesse no navegador:")
        print("https://sua-url.railway.app/admin/migrate_db")
        return False

if __name__ == "__main__":
    fix_railway()