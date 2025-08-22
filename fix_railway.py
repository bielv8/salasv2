"""
SCRIPT PARA CORRIGIR RAILWAY - Execute este comando no terminal do Railway:

python fix_railway.py

Ou acesse no navegador: sua-url.railway.app/admin/migrate_db
"""

from app import app, db
from sqlalchemy import text
import os

def fix_railway_database():
    """Corrige o banco PostgreSQL no Railway"""
    print("🔧 INICIANDO CORREÇÃO RAILWAY...")
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'Não definida')}")
    
    with app.app_context():
        try:
            print("Conectando ao banco...")
            
            with db.engine.connect() as conn:
                # Verificar tipo de banco
                db_url = str(db.engine.url)
                if 'postgres' in db_url:
                    print("✅ PostgreSQL detectado")
                    
                    # Comando específico para PostgreSQL
                    sql_commands = [
                        "ALTER TABLE incident ADD COLUMN IF NOT EXISTS hidden_from_classroom BOOLEAN DEFAULT FALSE;",
                        "UPDATE incident SET hidden_from_classroom = FALSE WHERE hidden_from_classroom IS NULL;"
                    ]
                    
                    for cmd in sql_commands:
                        try:
                            print(f"Executando: {cmd}")
                            conn.execute(text(cmd))
                            print("✅ Comando executado")
                        except Exception as e:
                            print(f"Info: {e}")
                    
                    conn.commit()
                    print("✅ Migração commitada")
                    
                    # Testar se funciona
                    result = conn.execute(text("SELECT COUNT(*) FROM incident WHERE hidden_from_classroom IS NOT NULL"))
                    count = result.scalar()
                    print(f"✅ Teste: {count} registros com hidden_from_classroom")
                    
                else:
                    print("SQLite detectado - usando comando alternativo")
                    conn.execute(text("ALTER TABLE incident ADD COLUMN hidden_from_classroom BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                    
                print("🎉 CORREÇÃO CONCLUÍDA!")
                print("Agora o painel de ocorrências deve funcionar!")
                return True
                
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False

if __name__ == "__main__":
    success = fix_railway_database()
    if success:
        print("\n✅ SUCESSO! Sistema corrigido para Railway!")
        print("Acesse: /incidents_management")
    else:
        print("\n❌ FALHA! Contacte o suporte.")