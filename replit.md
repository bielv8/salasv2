# Overview

This is a classroom management system for SENAI "Morvan Figueiredo" school built with Flask. The system provides a digital map of classrooms showing their details, equipment, capacity, and availability. It includes features for viewing classroom information, managing schedules, generating reports, QR code generation for easy access to classroom details, advanced dashboard with filters, and Excel export functionality.

## Recent Updates (August 2025)
- **Migration to Replit Environment**: Successfully migrated from Replit Agent to standard Replit environment with improved security and Flask best practices
- **Excel File Management**: Added functionality for each classroom to have an associated Excel file that users can download
- **Enhanced Dashboard**: Added advanced filtering system with search by block, floor, capacity, computers, day, and shift
- **Excel Export**: Implemented comprehensive Excel export with multiple sheets (classrooms, schedules, statistics) and filtered export options
- **Improved PDF Generation**: Enhanced PDF reports with better formatting and error handling
- **Session Security**: Configured proper SESSION_SECRET for secure authentication
- **Schedule Management in Edit Page**: Added functionality to view and remove individual schedules directly from classroom edit page

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask web framework with Python
- **Database**: SQLAlchemy ORM with SQLite as default database (configurable via DATABASE_URL environment variable)
- **Authentication**: Simple password-based admin authentication using Flask sessions
- **Model Structure**: Two main entities - Classroom and Schedule with proper foreign key relationships

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **Styling**: Custom CSS with SENAI branding colors and responsive design
- **JavaScript**: Vanilla JavaScript for form enhancements, tooltips, and interactive features
- **UI Framework**: Bootstrap 5 with Font Awesome icons

## Data Storage
- **Primary Database**: SQLite for development, configurable for production databases
- **Session Management**: Flask sessions with configurable secret key
- **Connection Pooling**: SQLAlchemy engine with connection recycling and pre-ping enabled

## Authentication & Authorization
- **Admin Access**: Simple password-based authentication (password: "senai103103")
- **Session Management**: 2-hour session timeout for admin users
- **Route Protection**: Decorator-based protection for admin-only routes
- **Public Access**: Read-only access to classroom information without authentication

## Core Features
- **Classroom Management**: CRUD operations for classroom information including capacity, equipment, and location
- **Excel File Management**: Each classroom can have an associated Excel file for download by users
- **Schedule Management**: Admin can manage class schedules with different shifts (morning, afternoon, full-day, night) including individual schedule removal from classroom edit page
- **Availability Tracking**: Real-time display of classroom availability based on scheduled classes
- **Report Generation**: PDF report generation using ReportLab library
- **QR Code Generation**: Dynamic QR code creation for classroom access using qrcode and PIL libraries

## File Organization
- **app.py**: Main application configuration and database initialization
- **models.py**: Database models for Classroom and Schedule entities
- **routes.py**: All route handlers and view logic
- **pdf_generator.py**: PDF report generation functionality
- **qr_generator.py**: QR code creation utilities
- **templates/**: Jinja2 HTML templates with consistent base layout
- **static/**: CSS and JavaScript assets with custom SENAI styling

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web framework for Python applications
- **Flask-SQLAlchemy**: Database ORM integration with Flask
- **SQLAlchemy**: Database toolkit and ORM

## Document Generation
- **ReportLab**: PDF generation library for creating formatted reports
- **qrcode**: QR code generation library
- **Pillow (PIL)**: Image processing for QR code enhancement

## Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme variant from Replit CDN
- **Font Awesome 6**: Icon library for UI elements

## Development Dependencies
- **Logging**: Python's built-in logging for debugging and monitoring
- **Environment Variables**: Configuration management for database URLs and session secrets

## Database Configuration
- **Default**: SQLite database (senai_classrooms.db)
- **Production**: Configurable via DATABASE_URL environment variable
- **Connection Management**: Pool recycling and connection health checks enabled