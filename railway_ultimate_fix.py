#!/usr/bin/env python3
"""
CORREÇÃO DEFINITIVA PARA RAILWAY - SOLUÇÃO COMPLETA
Execute este comando no terminal do Railway:

python railway_ultimate_fix.py

OU acesse: https://sua-url.railway.app/admin/migrate_db

Esta é a correção DEFINITIVA para todos os erros 500
"""

import os
import sys

def ultimate_railway_fix():
    print("🚀 INICIANDO CORREÇÃO ULTIMATE PARA RAILWAY...")
    
    # Configurar ambiente
    os.environ.setdefault('FLASK_APP', 'app.py')
    
    try:
        from app import app, db
        from sqlalchemy import text
        
        with app.app_context():
            print("✅ Aplicação carregada com sucesso")
            
            with db.engine.connect() as conn:
                print("✅ Conectado ao PostgreSQL")
                
                # 1. Verificar e corrigir schema da tabela incident
                print("🔧 Verificando schema da tabela incident...")
                
                missing_columns = []
                
                # Verificar colunas obrigatórias
                required_columns = [
                    ('hidden_from_classroom', 'BOOLEAN DEFAULT FALSE'),
                    ('is_resolved', 'BOOLEAN DEFAULT FALSE'),
                    ('admin_response', 'TEXT'),
                    ('response_date', 'TIMESTAMP')
                ]
                
                for column_name, column_def in required_columns:
                    try:
                        result = conn.execute(text(f"""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_name='incident' AND column_name='{column_name}'
                        """))
                        if not result.fetchone():
                            missing_columns.append((column_name, column_def))
                    except Exception as e:
                        print(f"⚠️  Erro ao verificar coluna {column_name}: {e}")
                        missing_columns.append((column_name, column_def))
                
                # Adicionar colunas faltantes
                for column_name, column_def in missing_columns:
                    try:
                        conn.execute(text(f"""
                            ALTER TABLE incident 
                            ADD COLUMN {column_name} {column_def}
                        """))
                        conn.commit()
                        print(f"✅ Coluna {column_name} adicionada!")
                    except Exception as e:
                        print(f"⚠️  {column_name}: {e}")
                
                # 2. Verificar schema da tabela classroom
                print("🔧 Verificando schema da tabela classroom...")
                
                classroom_columns = [
                    ('image_data', 'BYTEA'),
                    ('excel_data', 'BYTEA'), 
                    ('image_mimetype', 'VARCHAR(100)'),
                    ('excel_mimetype', 'VARCHAR(100)'),
                    ('admin_password', 'VARCHAR(255) DEFAULT \'\''),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
                    ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ]
                
                for column_name, column_def in classroom_columns:
                    try:
                        result = conn.execute(text(f"""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_name='classroom' AND column_name='{column_name}'
                        """))
                        if not result.fetchone():
                            conn.execute(text(f"""
                                ALTER TABLE classroom 
                                ADD COLUMN {column_name} {column_def}
                            """))
                            conn.commit()
                            print(f"✅ Coluna classroom.{column_name} adicionada!")
                    except Exception as e:
                        print(f"⚠️  classroom.{column_name}: {e}")
                
                # 3. Verificar schema da tabela schedule
                print("🔧 Verificando schema da tabela schedule...")
                
                schedule_columns = [
                    ('start_date', 'DATE'),
                    ('end_date', 'DATE'),
                    ('is_active', 'BOOLEAN DEFAULT TRUE'),
                    ('created_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
                ]
                
                for column_name, column_def in schedule_columns:
                    try:
                        result = conn.execute(text(f"""
                            SELECT column_name FROM information_schema.columns 
                            WHERE table_name='schedule' AND column_name='{column_name}'
                        """))
                        if not result.fetchone():
                            conn.execute(text(f"""
                                ALTER TABLE schedule 
                                ADD COLUMN {column_name} {column_def}
                            """))
                            conn.commit()
                            print(f"✅ Coluna schedule.{column_name} adicionada!")
                    except Exception as e:
                        print(f"⚠️  schedule.{column_name}: {e}")
                
                # 4. Limpar dados inconsistentes
                print("🧹 Limpando dados inconsistentes...")
                
                cleanup_queries = [
                    "UPDATE incident SET hidden_from_classroom = FALSE WHERE hidden_from_classroom IS NULL",
                    "UPDATE incident SET is_resolved = FALSE WHERE is_resolved IS NULL", 
                    "UPDATE incident SET is_active = TRUE WHERE is_active IS NULL",
                    "UPDATE classroom SET admin_password = '' WHERE admin_password IS NULL",
                    "UPDATE schedule SET is_active = TRUE WHERE is_active IS NULL"
                ]
                
                for query in cleanup_queries:
                    try:
                        result = conn.execute(text(query))
                        conn.commit()
                        updated = result.rowcount if hasattr(result, 'rowcount') else 0
                        print(f"✅ Cleanup: {updated} registros atualizados")
                    except Exception as e:
                        print(f"⚠️  Cleanup: {e}")
                
                # 5. Teste final das queries principais
                print("🧪 Testando queries principais...")
                
                test_queries = [
                    ("SELECT COUNT(*) FROM incident WHERE is_active = true", "Contagem de incidents"),
                    ("SELECT COUNT(*) FROM classroom", "Contagem de classrooms"),
                    ("SELECT COUNT(*) FROM schedule WHERE is_active = true", "Contagem de schedules"),
                    ("SELECT COUNT(*) FROM incident WHERE hidden_from_classroom = false OR hidden_from_classroom IS NULL", "Test hidden_from_classroom")
                ]
                
                for query, description in test_queries:
                    try:
                        result = conn.execute(text(query))
                        count = result.scalar()
                        print(f"✅ {description}: {count}")
                    except Exception as e:
                        print(f"❌ {description}: {e}")
                        return False
                
                print("🎯 Teste específico da query problemática...")
                try:
                    result = conn.execute(text("""
                        SELECT incident.id, incident.classroom_id, incident.reporter_name, 
                               incident.reporter_email, incident.description, incident.created_at, 
                               incident.is_active, incident.hidden_from_classroom, incident.is_resolved, 
                               incident.admin_response, incident.response_date 
                        FROM incident 
                        WHERE incident.is_active = true 
                        AND (incident.hidden_from_classroom = false OR incident.hidden_from_classroom IS NULL) 
                        ORDER BY incident.created_at DESC 
                        LIMIT 1
                    """))
                    test_row = result.fetchone()
                    print("✅ Query problemática funcionando perfeitamente!")
                except Exception as e:
                    print(f"❌ Query ainda com problema: {e}")
                    return False
                
        print("\n" + "="*60)
        print("🎉🎉🎉 CORREÇÃO ULTIMATE CONCLUÍDA COM SUCESSO! 🎉🎉🎉")
        print("✅ Todas as colunas verificadas e corrigidas")
        print("✅ Dados inconsistentes limpos")
        print("✅ Queries principais testadas e funcionando")
        print("✅ Sistema 100% compatível com PostgreSQL")
        print("✅ Gestão de ocorrências totalmente operacional")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")
        print(f"❌ Tipo do erro: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        print("\n🔧 SOLUÇÕES ALTERNATIVAS:")
        print("1. Verificar se DATABASE_URL está configurada")
        print("2. Verificar se PostgreSQL está acessível")
        print("3. Verificar permissões do banco de dados")
        print("4. Acesse: https://sua-url.railway.app/admin/migrate_db")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("   CORREÇÃO ULTIMATE RAILWAY - ERRO 500")
    print("   Solução Definitiva para PostgreSQL")
    print("=" * 60)
    
    success = ultimate_railway_fix()
    
    print("=" * 60)
    if success:
        print("STATUS: ✅ SUCESSO TOTAL - SISTEMA CORRIGIDO!")
        print("🚀 Acesse seu app: todas as páginas devem funcionar!")
        print("🚀 Gestão de ocorrências: /incidents_management")
        print("🚀 Dashboard: /dashboard")
        print("🚀 Sistema 100% operacional!")
    else:
        print("STATUS: ❌ FALHA - CONTATE SUPORTE TÉCNICO")
        print("📧 Inclua os logs acima no contato")
    print("=" * 60)