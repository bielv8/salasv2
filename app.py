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
app.secret_key = os.environ.get("SESSION_SECRET")
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
    
    # Drop and recreate tables to handle schema changes
    db.drop_all()
    db.create_all()
    
    # Initialize sample data
    try:
        sample_classrooms = [
            {
                'name': 'Laboratório de Informática 1',
                'capacity': 30,
                'has_computers': True,
                'software': 'Windows 10, Office 365, AutoCAD, SolidWorks',
                'description': 'Laboratório equipado com computadores de última geração para cursos técnicos.',
                'floor': 1,
                'block': 'A',
                'image_url': ''
            },
            {
                'name': 'Sala de Aula 101',
                'capacity': 25,
                'has_computers': False,
                'software': '',
                'description': 'Sala de aula tradicional com projetor e ar condicionado.',
                'floor': 1,
                'block': 'A',
                'image_url': ''
            },
            {
                'name': 'Laboratório de Eletrônica',
                'capacity': 20,
                'has_computers': True,
                'software': 'Proteus, Multisim, LabVIEW',
                'description': 'Laboratório especializado em eletrônica com bancadas e equipamentos.',
                'floor': 2,
                'block': 'B',
                'image_url': ''
            },
            {
                'name': 'Sala de Aula 201',
                'capacity': 35,
                'has_computers': False,
                'software': '',
                'description': 'Sala ampla para aulas teóricas com sistema de som.',
                'floor': 2,
                'block': 'B',
                'image_url': ''
            },
            {
                'name': 'Laboratório de Mecânica',
                'capacity': 15,
                'has_computers': True,
                'software': 'AutoCAD Mechanical, Inventor, ANSYS',
                'description': 'Laboratório para cursos de mecânica com simuladores.',
                'floor': 1,
                'block': 'C',
                'image_url': ''
            }
        ]
        
        for classroom_data in sample_classrooms:
            classroom = models.Classroom(**classroom_data)
            db.session.add(classroom)
        
        db.session.commit()
        print("Sample classrooms created successfully!")
    except Exception as e:
        print(f"Database setup completed: {e}")

# Import routes
import routes
