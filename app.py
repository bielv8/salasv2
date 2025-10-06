import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "senai_classroom_secret_key_2025_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///senai_classrooms.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "connect_args": {"client_encoding": "utf8"} if "postgresql" in os.environ.get("DATABASE_URL", "") else {}
}

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    try:
        # Import models to ensure tables are created
        import models
        
        # Test database connection first
        from sqlalchemy import text
        print(f"Testing database connection to: {app.config['SQLALCHEMY_DATABASE_URI'][:20]}...")
        with db.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        import logging
        logging.info("Database connection successful!")
        
        # Create tables if they don't exist
        db.create_all()
        logging.info("Tables created/verified successfully!")
        
        # Add new columns if they don't exist (for existing databases)
        try:
            from sqlalchemy import text
            with db.engine.connect() as conn:
                # Check if new columns exist, if not add them (PostgreSQL compatible)
                try:
                    conn.execute(text("ALTER TABLE classroom ADD COLUMN image_data BYTEA"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE classroom ADD COLUMN excel_data BYTEA"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE classroom ADD COLUMN image_mimetype VARCHAR(100)"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE classroom ADD COLUMN excel_mimetype VARCHAR(100)"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE incident ADD COLUMN is_resolved BOOLEAN DEFAULT FALSE"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE incident ADD COLUMN admin_response TEXT"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE incident ADD COLUMN response_date TIMESTAMP"))
                except:
                    pass  # Column already exists
                # Add hidden_from_classroom column with better error handling
                try:
                    # Different checks for different database types
                    db_url_str = str(db.engine.url)
                    column_exists = False
                    
                    if 'postgresql' in db_url_str or 'postgres' in db_url_str:
                        # PostgreSQL check
                        try:
                            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='incident' AND column_name='hidden_from_classroom'"))
                            column_exists = result.fetchone() is not None
                        except:
                            column_exists = False
                    else:
                        # SQLite check - try to select the column
                        try:
                            conn.execute(text("SELECT hidden_from_classroom FROM incident LIMIT 1"))
                            column_exists = True
                        except:
                            column_exists = False
                    
                    if not column_exists:
                        # Add the column
                        conn.execute(text("ALTER TABLE incident ADD COLUMN hidden_from_classroom BOOLEAN DEFAULT FALSE"))
                        conn.commit()
                        logging.info("✅ Added hidden_from_classroom column")
                    else:
                        logging.info("✅ hidden_from_classroom column already exists")
                        
                except Exception as col_error:
                    # Final fallback: ignore if column already exists error
                    logging.warning(f"Column migration info: {col_error}")
                    pass
                
                # Add schedule columns to class_group table
                try:
                    conn.execute(text("ALTER TABLE class_group ADD COLUMN shift VARCHAR(20) DEFAULT ''"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE class_group ADD COLUMN start_time VARCHAR(10) DEFAULT ''"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE class_group ADD COLUMN end_time VARCHAR(10) DEFAULT ''"))
                except:
                    pass  # Column already exists
                try:
                    conn.execute(text("ALTER TABLE class_group ADD COLUMN days_of_week TEXT DEFAULT ''"))
                except:
                    pass  # Column already exists
                
                conn.commit()
        except Exception as migration_error:
            import logging
            logging.warning(f"Database migration error (non-critical): {migration_error}")
            import traceback
            traceback.print_exc()
        
        # Initialize sample data ONLY if no classrooms exist
        existing_classrooms = models.Classroom.query.first()
        if not existing_classrooms:
            try:
                # Create sample classrooms with explicit UTF-8 encoding
                sample_classrooms = [
                    {
                        'name': 'Laboratorio de Jogos Digitais',
                        'capacity': 34,
                        'has_computers': True,
                        'software': 'Unity, Unreal Engine, Blender',
                        'description': 'Laboratorio especializado para desenvolvimento de jogos digitais.',
                        'block': 'Oficina 1',
                        'image_filename': ''
                    },
                    {
                        'name': 'SALA DEV',
                        'capacity': 34,
                        'has_computers': True,
                        'software': 'Visual Studio, Git, Docker',
                        'description': 'Sala de desenvolvimento de sistemas.',
                        'block': 'Oficina 2',
                        'image_filename': ''
                    },
                    {
                        'name': 'Sala 208',
                        'capacity': 34,
                        'has_computers': True,
                        'software': 'IDE, Banco de dados',
                        'description': 'Sala para desenvolvimento e banco de dados.',
                        'block': 'Bloco A',
                        'image_filename': ''
                    },
                    {
                        'name': 'Sala 202',
                        'capacity': 20,
                        'has_computers': True,
                        'software': 'Office, Visual Studio',
                        'description': 'Sala para cursos FIC e desenvolvimento.',
                        'block': 'Bloco A',
                        'image_filename': ''
                    }
                ]
                
                for classroom_data in sample_classrooms:
                    classroom = models.Classroom(**classroom_data)
                    db.session.add(classroom)
                
                db.session.commit()
                logging.info("Sample classrooms created successfully!")
            except Exception as e:
                logging.error(f"Error creating sample data: {e}")
                import traceback
                traceback.print_exc()
                db.session.rollback()
        else:
            logging.info("Database already has data, skipping sample creation")
            
    except Exception as e:
        import logging
        logging.error(f"CRITICAL ERROR initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continue anyway, routes might still work

# Import routes after app initialization to avoid circular imports
try:
    import routes
except Exception as e:
    import logging
    logging.error(f"Error importing routes: {str(e)}")
    raise e