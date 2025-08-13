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
app.secret_key = os.environ.get("SESSION_SECRET", "senai-morvan-figueiredo-2024-secret-key-123456789")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///senai_classrooms.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    
    # Create tables if they don't exist
    db.create_all()
    
    # Initialize sample data ONLY if no classrooms exist
    existing_classrooms = models.Classroom.query.first()
    if not existing_classrooms:
        try:
            sample_classrooms = [
            {
                'name': 'Laboratório de Jogos Digitais',
                'capacity': 34,
                'has_computers': True,
                'software': 'Unity, Unreal Engine, Blender',
                'description': 'Laboratório especializado para desenvolvimento de jogos digitais.',
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
            print("Sample classrooms created successfully!")
        except Exception as e:
            print(f"Error creating sample data: {e}")
    else:
        print("Database already has data, skipping sample creation")

# Import routes
import routes
