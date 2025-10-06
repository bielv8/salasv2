from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    has_computers = db.Column(db.Boolean, default=False)
    software = db.Column(db.Text, default='')
    description = db.Column(db.Text, default='')
    block = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(255), default='')  # Store filename instead of URL
    excel_filename = db.Column(db.String(255), default='')  # Store Excel filename
    image_data = db.Column(db.LargeBinary)  # Store image data in PostgreSQL (BYTEA)
    excel_data = db.Column(db.LargeBinary)  # Store Excel file data in PostgreSQL (BYTEA)
    image_mimetype = db.Column(db.String(100))  # Store image MIME type
    excel_mimetype = db.Column(db.String(100))  # Store Excel MIME type
    admin_password = db.Column(db.String(255), default='')  # Admin password for classroom access
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, name='', capacity=0, has_computers=False, software='', description='', block='', image_filename='', excel_filename='', admin_password=''):
        self.name = name
        self.capacity = capacity
        self.has_computers = has_computers
        self.software = software
        self.description = description
        self.block = block
        self.image_filename = image_filename
        self.excel_filename = excel_filename
        self.admin_password = admin_password
    
    # Relationship with schedules
    schedules = db.relationship('Schedule', backref='classroom', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Classroom {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity,
            'has_computers': self.has_computers,
            'software': self.software,
            'description': self.description,
            'block': self.block,
            'excel_filename': self.excel_filename
        }

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    shift = db.Column(db.String(20), nullable=False)  # morning, afternoon, fullday, night
    course_name = db.Column(db.String(100), nullable=False)
    instructor = db.Column(db.String(100), default='')
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    start_date = db.Column(db.Date, nullable=True)  # Course start date
    end_date = db.Column(db.Date, nullable=True)    # Course end date
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, classroom_id=0, day_of_week=0, shift='', course_name='', instructor='', start_time='', end_time='', start_date=None, end_date=None, is_active=True):
        self.classroom_id = classroom_id
        self.day_of_week = day_of_week
        self.shift = shift
        self.course_name = course_name
        self.instructor = instructor
        self.start_time = start_time
        self.end_time = end_time
        self.start_date = start_date
        self.end_date = end_date
        self.is_active = is_active
    
    def __repr__(self):
        return f'<Schedule {self.course_name} - {self.shift}>'
    
    def to_dict(self):
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'day_of_week': self.day_of_week,
            'day_name': days[self.day_of_week],
            'shift': self.shift,
            'course_name': self.course_name,
            'instructor': self.instructor,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else '',
            'is_active': self.is_active
        }

class AdminSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    reporter_name = db.Column(db.String(100), nullable=False)
    reporter_email = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    hidden_from_classroom = db.Column(db.Boolean, default=False)
    is_resolved = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    
    # Relationship with classroom
    classroom = db.relationship('Classroom', backref='incidents')
    
    def __init__(self, classroom_id=0, reporter_name='', reporter_email='', description=''):
        self.classroom_id = classroom_id
        self.reporter_name = reporter_name
        self.reporter_email = reporter_email
        self.description = description
        self.is_resolved = False
        self.hidden_from_classroom = False
    
    def to_dict(self):
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'classroom_name': self.classroom.name if self.classroom else 'Sala não encontrada',
            'reporter_name': self.reporter_name,
            'reporter_email': self.reporter_email,
            'description': self.description,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M') if self.created_at else '',
            'is_active': self.is_active,
            'is_resolved': self.is_resolved,
            'admin_response': self.admin_response,
            'response_date': self.response_date.strftime('%d/%m/%Y às %H:%M') if self.response_date else ''
        }
    
    def __repr__(self):
        return f'<Incident {self.id} - {self.reporter_name}>'

class ScheduleRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(100), nullable=False)
    requester_phone = db.Column(db.String(20), default='')
    organization = db.Column(db.String(100), default='')
    event_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Schedule details
    requested_date = db.Column(db.Date, nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 1=Tuesday, ..., 6=Sunday
    shift = db.Column(db.String(20), nullable=False)  # morning, afternoon, fullday, night
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    
    # Bulk request support - for multiple dates
    additional_dates = db.Column(db.Text, default='')  # JSON string with additional dates
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text, default='')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by = db.Column(db.String(100), default='')
    
    # Relationship with classroom
    classroom = db.relationship('Classroom', backref='schedule_requests')
    
    def __init__(self, classroom_id=0, requester_name='', requester_email='', 
                 event_name='', description='', requested_date=None, 
                 day_of_week=0, shift='', start_time='', end_time='', additional_dates=''):
        self.classroom_id = classroom_id
        self.requester_name = requester_name
        self.requester_email = requester_email
        self.requester_phone = ''  # Keep for compatibility but not required
        self.organization = ''  # Keep for compatibility but not required
        self.event_name = event_name
        self.description = description
        self.requested_date = requested_date
        self.day_of_week = day_of_week
        self.shift = shift
        self.start_time = start_time
        self.end_time = end_time
        self.additional_dates = additional_dates
        self.status = 'pending'
    
    def to_dict(self):
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'classroom_name': self.classroom.name if self.classroom else 'Sala não encontrada',
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'event_name': self.event_name,
            'description': self.description,
            'requested_date': self.requested_date.strftime('%d/%m/%Y') if self.requested_date else '',
            'day_of_week': self.day_of_week,
            'shift': self.shift,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'additional_dates': self.additional_dates,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M') if self.created_at else '',
            'reviewed_at': self.reviewed_at.strftime('%d/%m/%Y às %H:%M') if self.reviewed_at else '',
            'reviewed_by': self.reviewed_by
        }
    
    def __repr__(self):
        return f'<ScheduleRequest {self.id} - {self.event_name}>'

class_group_teachers = db.Table('class_group_teachers',
    db.Column('class_group_id', db.Integer, db.ForeignKey('class_group.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class ClassGroup(db.Model):
    """Represents a class/group of students for asset management"""
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)  # Nome da turma
    excel_filename = db.Column(db.String(255), default='')
    excel_data = db.Column(db.LargeBinary)  # Store Excel file
    excel_mimetype = db.Column(db.String(100))
    
    # Schedule information
    shift = db.Column(db.String(20), default='')  # morning, afternoon, night, fullday
    start_time = db.Column(db.String(10), default='')  # e.g., "08:00"
    end_time = db.Column(db.String(10), default='')  # e.g., "12:00"
    days_of_week = db.Column(db.Text, default='')  # JSON array: [0,1,2,3,4] for Mon-Fri
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = db.relationship('Classroom', backref=db.backref('class_groups', lazy=True, cascade='all, delete-orphan'))
    teacher = db.relationship('User', backref=db.backref('class_groups', lazy=True), foreign_keys=[teacher_id])
    teachers = db.relationship('User', secondary=class_group_teachers, backref=db.backref('teaching_groups', lazy='dynamic'))
    students = db.relationship('Student', backref='class_group', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<ClassGroup {self.name}>'
    
    def is_active_now(self, current_time=None, current_day=None):
        """Check if this class group is currently in session"""
        if not self.shift or not self.start_time or not self.end_time:
            return False
        
        if current_time is None:
            current_time = datetime.utcnow()
        if current_day is None:
            current_day = current_time.weekday()
        
        # Check if current day is in the schedule
        if self.days_of_week:
            try:
                import json
                scheduled_days = json.loads(self.days_of_week)
                if str(current_day) not in scheduled_days:
                    return False
            except:
                return False
        
        # Check if current time is within class hours
        try:
            from datetime import time
            start_parts = self.start_time.split(':')
            end_parts = self.end_time.split(':')
            
            start = time(int(start_parts[0]), int(start_parts[1]))
            end = time(int(end_parts[0]), int(end_parts[1]))
            current = current_time.time()
            
            if end < start:
                return current >= start or current <= end
            return start <= current <= end
        except:
            return False
    
    def to_dict(self):
        teacher_names = [t.name for t in self.teachers] if self.teachers else []
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'name': self.name,
            'excel_filename': self.excel_filename,
            'student_count': len(self.students) if self.students else 0,
            'shift': self.shift,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'days_of_week': self.days_of_week,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M') if self.created_at else '',
            'is_active_now': self.is_active_now(),
            'teachers': teacher_names,
            'teacher_names': ', '.join(teacher_names) if teacher_names else 'Sem docente atribuído'
        }

class Student(db.Model):
    """Represents an individual student in a class group"""
    id = db.Column(db.Integer, primary_key=True)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    row_number = db.Column(db.Integer)  # Original row in Excel for reference
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, class_group_id=0, name='', row_number=None):
        self.class_group_id = class_group_id
        self.name = name
        self.row_number = row_number
    
    def __repr__(self):
        return f'<Student {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'class_group_id': self.class_group_id,
            'name': self.name,
            'row_number': self.row_number
        }

class ClassroomLayout(db.Model):
    """Stores the layout design for a classroom"""
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False, unique=True)
    layout_data = db.Column(db.Text)  # JSON with grid dimensions and metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    classroom = db.relationship('Classroom', backref=db.backref('layout', uselist=False, cascade='all, delete-orphan'))
    workstations = db.relationship('Workstation', backref='layout', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, classroom_id=0):
        self.classroom_id = classroom_id
    
    def __repr__(self):
        return f'<ClassroomLayout for {self.classroom.name if self.classroom else "Unknown"}>'

class Workstation(db.Model):
    """Represents a numbered workstation/PC in the layout"""
    id = db.Column(db.Integer, primary_key=True)
    layout_id = db.Column(db.Integer, db.ForeignKey('classroom_layout.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)  # PC number
    position_x = db.Column(db.Integer, nullable=False)  # Grid X position
    position_y = db.Column(db.Integer, nullable=False)  # Grid Y position
    notes = db.Column(db.Text, default='')  # Observações sobre o PC
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assignments = db.relationship('WorkstationAssignment', backref='workstation', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, layout_id=0, number=0, position_x=0, position_y=0, notes=''):
        self.layout_id = layout_id
        self.number = number
        self.position_x = position_x
        self.position_y = position_y
        self.notes = notes
    
    def __repr__(self):
        return f'<Workstation #{self.number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'position_x': self.position_x,
            'position_y': self.position_y,
            'notes': self.notes
        }

class WorkstationAssignment(db.Model):
    """Links students to workstations for a specific class group"""
    id = db.Column(db.Integer, primary_key=True)
    workstation_id = db.Column(db.Integer, db.ForeignKey('workstation.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    class_group = db.relationship('ClassGroup', backref='assignments')
    student = db.relationship('Student', backref='assignments')
    
    # Unique constraint: each student can only be assigned to one workstation per class group
    __table_args__ = (
        db.UniqueConstraint('student_id', 'class_group_id', name='unique_student_class'),
    )
    
    def __init__(self, workstation_id=0, class_group_id=0, student_id=0):
        self.workstation_id = workstation_id
        self.class_group_id = class_group_id
        self.student_id = student_id
    
    def __repr__(self):
        return f'<WorkstationAssignment W#{self.workstation_id} -> Student#{self.student_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'workstation_id': self.workstation_id,
            'class_group_id': self.class_group_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else ''
        }

class AttendanceSession(db.Model):
    """Represents an attendance session for a class group on a specific date"""
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
    created_by = db.Column(db.String(100), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    classroom = db.relationship('Classroom', backref='attendance_sessions')
    class_group = db.relationship('ClassGroup', backref='attendance_sessions')
    records = db.relationship('AttendanceRecord', backref='session', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, classroom_id=0, class_group_id=0, session_date=None, status='active', created_by=''):
        self.classroom_id = classroom_id
        self.class_group_id = class_group_id
        self.session_date = session_date
        self.status = status
        self.created_by = created_by
    
    def __repr__(self):
        return f'<AttendanceSession {self.id} - {self.session_date}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'classroom_id': self.classroom_id,
            'classroom_name': self.classroom.name if self.classroom else '',
            'class_group_id': self.class_group_id,
            'class_group_name': self.class_group.name if self.class_group else '',
            'session_date': self.session_date.strftime('%Y-%m-%d') if self.session_date else '',
            'status': self.status,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M') if self.created_at else '',
            'total_students': len(self.records) if self.records else 0,
            'present_count': sum(1 for r in self.records if r.status == 'present') if self.records else 0,
            'absent_count': sum(1 for r in self.records if r.status == 'absent') if self.records else 0
        }

class AttendanceRecord(db.Model):
    """Records individual student attendance for a session"""
    id = db.Column(db.Integer, primary_key=True)
    attendance_session_id = db.Column(db.Integer, db.ForeignKey('attendance_session.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    workstation_id = db.Column(db.Integer, db.ForeignKey('workstation.id'), nullable=True)
    status = db.Column(db.String(20), default='absent')
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_out_time = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='attendance_records')
    workstation = db.relationship('Workstation', backref='attendance_records')
    
    def __init__(self, attendance_session_id=0, student_id=0, workstation_id=None, status='absent'):
        self.attendance_session_id = attendance_session_id
        self.student_id = student_id
        self.workstation_id = workstation_id
        self.status = status
    
    def __repr__(self):
        return f'<AttendanceRecord {self.id} - Student#{self.student_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'attendance_session_id': self.attendance_session_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else '',
            'workstation_id': self.workstation_id,
            'workstation_number': self.workstation.number if self.workstation else None,
            'status': self.status,
            'check_in_time': self.check_in_time.strftime('%H:%M:%S') if self.check_in_time else '',
            'check_out_time': self.check_out_time.strftime('%H:%M:%S') if self.check_out_time else '',
            'notes': self.notes
        }

class User(db.Model, UserMixin):
    """User model for authentication with roles"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='teacher')  # 'admin' or 'teacher'
    email = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    first_login = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __init__(self, username='', name='', role='teacher', email='', first_login=True):
        self.username = username
        self.name = name
        self.role = role
        self.email = email
        self.is_active = True
        self.first_login = first_login
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_teacher(self):
        return self.role == 'teacher'
    
    def get_id(self):
        """Required method for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'role': self.role,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%d/%m/%Y às %H:%M') if self.created_at else ''
        }
