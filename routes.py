import os
from flask import render_template, request, redirect, url_for, flash, session, jsonify, send_file, make_response
from app import app, db
from models import Classroom, Schedule, AdminSession
from datetime import datetime, timedelta
from pdf_generator import generate_classroom_pdf, generate_general_report, generate_availability_report
from qr_generator import generate_qr_code
import io
from urllib.parse import urljoin
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from werkzeug.utils import secure_filename
import uuid

ADMIN_PASSWORD = "senai103103"
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin_authenticated():
    return session.get('admin_authenticated', False)

def require_admin_auth(f):
    def decorated_function(*args, **kwargs):
        if not is_admin_authenticated():
            flash('Acesso negado. Autenticação necessária.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    classrooms = Classroom.query.all()
    return render_template('index.html', classrooms=classrooms)

@app.route('/classroom/<int:classroom_id>')
def classroom_detail(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    schedules = Schedule.query.filter_by(classroom_id=classroom_id, is_active=True).all()
    return render_template('classroom.html', classroom=classroom, schedules=schedules)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=2)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Senha incorreta!', 'error')
    
    return render_template('auth.html')

@app.route('/logout')
def logout():
    session.pop('admin_authenticated', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/edit_classroom/<int:classroom_id>', methods=['GET', 'POST'])
@require_admin_auth
def edit_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    if request.method == 'POST':
        classroom.name = request.form.get('name', '')
        classroom.capacity = int(request.form.get('capacity', 0))
        classroom.has_computers = 'has_computers' in request.form
        classroom.software = request.form.get('software', '')
        classroom.description = request.form.get('description', '')
        classroom.floor = int(request.form.get('floor', 1))
        classroom.block = request.form.get('block', '')
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add unique identifier to prevent conflicts
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                classroom.image_filename = unique_filename
        classroom.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Sala atualizada com sucesso!', 'success')
        return redirect(url_for('classroom_detail', classroom_id=classroom_id))
    
    return render_template('edit_classroom.html', classroom=classroom)

@app.route('/add_classroom', methods=['GET', 'POST'])
@require_admin_auth
def add_classroom():
    if request.method == 'POST':
        # Handle image upload
        image_filename = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add unique identifier to prevent conflicts
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                file.save(os.path.join(UPLOAD_FOLDER, unique_filename))
                image_filename = unique_filename
        
        classroom = Classroom(
            name=request.form.get('name', ''),
            capacity=int(request.form.get('capacity', 0)),
            has_computers='has_computers' in request.form,
            software=request.form.get('software', ''),
            description=request.form.get('description', ''),
            floor=int(request.form.get('floor', 1)),
            block=request.form.get('block', ''),
            image_filename=image_filename
        )
        
        db.session.add(classroom)
        db.session.commit()
        
        # Create initial schedules if provided
        initial_shift = request.form.get('initial_shift')
        if initial_shift and request.form.get('initial_course'):
            initial_days = request.form.getlist('initial_days')
            if initial_days:
                for day in initial_days:
                    schedule = Schedule(
                        classroom_id=classroom.id,
                        day_of_week=int(day),
                        shift=initial_shift,
                        course_name=request.form.get('initial_course', ''),
                        instructor=request.form.get('initial_instructor', ''),
                        start_time=request.form.get('initial_start_time', ''),
                        end_time=request.form.get('initial_end_time', '')
                    )
                    db.session.add(schedule)
                db.session.commit()
                flash(f'Sala adicionada com {len(initial_days)} horários iniciais!', 'success')
            else:
                flash('Sala adicionada com sucesso!', 'success')
        else:
            flash('Sala adicionada com sucesso!', 'success')
        
        return redirect(url_for('index'))
    
    return render_template('edit_classroom.html', classroom=None)

@app.route('/schedule_management')
@require_admin_auth
def schedule_management():
    classrooms = Classroom.query.all()
    schedules = Schedule.query.filter_by(is_active=True).all()
    return render_template('schedule_management.html', classrooms=classrooms, schedules=schedules)

@app.route('/add_schedule', methods=['POST'])
@require_admin_auth
def add_schedule():
    schedule = Schedule(
        classroom_id=int(request.form.get('classroom_id', 0)),
        day_of_week=int(request.form.get('day_of_week', 0)),
        shift=request.form.get('shift', ''),
        course_name=request.form.get('course_name', ''),
        instructor=request.form.get('instructor', ''),
        start_time=request.form.get('start_time', ''),
        end_time=request.form.get('end_time', '')
    )
    
    db.session.add(schedule)
    db.session.commit()
    flash('Horário adicionado com sucesso!', 'success')
    return redirect(url_for('schedule_management'))

@app.route('/batch_schedule', methods=['POST'])
@require_admin_auth
def batch_schedule():
    classroom_id = int(request.form.get('classroom_id', 0))
    course_name = request.form.get('course_name', '')
    instructor = request.form.get('instructor', '')
    shift = request.form.get('shift', '')
    start_time = request.form.get('start_time', '')
    end_time = request.form.get('end_time', '')
    
    # Get selected days
    selected_days = []
    for i in range(6):  # Monday to Saturday
        if request.form.get(f'day_{i}'):
            selected_days.append(i)
    
    if not selected_days:
        flash('Selecione pelo menos um dia da semana!', 'error')
        return redirect(url_for('schedule_management'))
    
    # Create schedules for selected days
    created_count = 0
    for day in selected_days:
        # Check if schedule already exists
        existing = Schedule.query.filter_by(
            classroom_id=classroom_id,
            day_of_week=day,
            shift=shift,
            is_active=True
        ).first()
        
        if not existing:
            schedule = Schedule(
                classroom_id=classroom_id,
                day_of_week=day,
                shift=shift,
                course_name=course_name,
                instructor=instructor,
                start_time=start_time,
                end_time=end_time
            )
            db.session.add(schedule)
            created_count += 1
    
    if created_count > 0:
        db.session.commit()
        flash(f'{created_count} horários adicionados com sucesso!', 'success')
    else:
        flash('Todos os horários selecionados já existem!', 'warning')
    
    return redirect(url_for('schedule_management'))

@app.route('/delete_schedule/<int:schedule_id>')
@require_admin_auth
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    schedule.is_active = False
    db.session.commit()
    flash('Horário removido com sucesso!', 'success')
    return redirect(url_for('schedule_management'))

@app.route('/dashboard')
def dashboard():
    # Get filter parameters
    block_filter = request.args.get('block', '')
    floor_filter = request.args.get('floor', '')
    has_computers_filter = request.args.get('has_computers', '')
    capacity_filter = request.args.get('capacity', '')
    day_filter = request.args.get('day', '')
    shift_filter = request.args.get('shift', '')
    
    # Build classroom query with filters
    classroom_query = Classroom.query
    if block_filter:
        classroom_query = classroom_query.filter(Classroom.block == block_filter)
    if floor_filter:
        classroom_query = classroom_query.filter(Classroom.floor == int(floor_filter))
    if has_computers_filter:
        has_computers_bool = has_computers_filter.lower() == 'true'
        classroom_query = classroom_query.filter(Classroom.has_computers == has_computers_bool)
    if capacity_filter:
        capacity_ranges = {
            'small': (0, 20),
            'medium': (21, 35),
            'large': (36, 100)
        }
        if capacity_filter in capacity_ranges:
            min_cap, max_cap = capacity_ranges[capacity_filter]
            classroom_query = classroom_query.filter(
                Classroom.capacity >= min_cap,
                Classroom.capacity <= max_cap
            )
    
    classrooms = classroom_query.all()
    
    # Build schedule query with filters
    schedule_query = Schedule.query.filter_by(is_active=True)
    if day_filter:
        schedule_query = schedule_query.filter(Schedule.day_of_week == int(day_filter))
    if shift_filter:
        schedule_query = schedule_query.filter(Schedule.shift == shift_filter)
    
    schedules = schedule_query.all()
    
    # Organize schedules by classroom and day
    schedule_map = {}
    for schedule in schedules:
        if schedule.classroom_id not in schedule_map:
            schedule_map[schedule.classroom_id] = {}
        if schedule.day_of_week not in schedule_map[schedule.classroom_id]:
            schedule_map[schedule.classroom_id][schedule.day_of_week] = {}
        schedule_map[schedule.classroom_id][schedule.day_of_week][schedule.shift] = schedule
    
    # Calculate statistics
    total_slots = len(classrooms) * 23  # 6 days * 4 shifts - 1 (no Saturday night)
    occupied_slots = len([s for s in schedules if s.classroom_id in [c.id for c in classrooms]])
    free_slots = total_slots - occupied_slots
    occupancy_rate = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
    
    # Get unique filter options
    all_classrooms = Classroom.query.all()
    blocks = sorted(list(set(c.block for c in all_classrooms if c.block)))
    floors = sorted(list(set(c.floor for c in all_classrooms)))
    
    return render_template('dashboard.html', 
                         classrooms=classrooms, 
                         schedule_map=schedule_map,
                         free_slots=free_slots,
                         occupied_slots=occupied_slots,
                         occupancy_rate=occupancy_rate,
                         blocks=blocks,
                         floors=floors,
                         current_filters={
                             'block': block_filter,
                             'floor': floor_filter,
                             'has_computers': has_computers_filter,
                             'capacity': capacity_filter,
                             'day': day_filter,
                             'shift': shift_filter
                         })

@app.route('/availability')
def availability():
    return redirect(url_for('dashboard'))

@app.route('/available_now')
def available_now():
    from datetime import datetime
    
    # Get current day and time
    current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
    current_hour = datetime.now().hour
    
    # Determine current shift
    current_shift = None
    if 7 <= current_hour < 12:
        current_shift = 'morning'
    elif 13 <= current_hour < 18:
        current_shift = 'afternoon'  
    elif 19 <= current_hour < 23:
        current_shift = 'night'
    elif 7 <= current_hour < 18:  # Full day overlaps with morning and afternoon
        current_shift = 'fullday'
    
    classrooms = Classroom.query.all()
    
    if current_day == 6 or current_shift is None:  # Sunday or outside operating hours
        available_rooms = classrooms
        current_period = "Fora do horário de funcionamento"
    else:
        # Find occupied classrooms for current time slot
        occupied_schedules = Schedule.query.filter_by(
            day_of_week=current_day,
            shift=current_shift,
            is_active=True
        ).all()
        
        occupied_classroom_ids = [s.classroom_id for s in occupied_schedules]
        available_rooms = [room for room in classrooms if room.id not in occupied_classroom_ids]
        
        days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        shifts = {'morning': 'Manhã', 'afternoon': 'Tarde', 'fullday': 'Integral', 'night': 'Noite'}
        current_period = f"{days[current_day]} - {shifts.get(current_shift, 'N/A')}"
    
    return render_template('available_now.html', 
                         available_rooms=available_rooms,
                         current_period=current_period,
                         total_rooms=len(classrooms))

@app.route('/generate_pdf/<int:classroom_id>')
def generate_pdf(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    schedules = Schedule.query.filter_by(classroom_id=classroom_id, is_active=True).all()
    
    pdf_buffer = generate_classroom_pdf(classroom, schedules)
    
    return send_file(
        io.BytesIO(pdf_buffer.getvalue()),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'sala_{classroom.name.replace(" ", "_")}.pdf'
    )

@app.route('/generate_general_report')  
def generate_general_report_route():
    classrooms = Classroom.query.all()
    all_schedules = Schedule.query.filter_by(is_active=True).all()
    
    pdf_buffer = generate_general_report(classrooms, all_schedules)
    
    return send_file(
        io.BytesIO(pdf_buffer.getvalue()),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='relatorio_geral_salas.pdf'
    )

@app.route('/generate_availability_report')
def generate_availability_report_route():
    classrooms = Classroom.query.all()
    schedules = Schedule.query.filter_by(is_active=True).all()
    
    pdf_buffer = generate_availability_report(classrooms, schedules)
    
    return send_file(
        io.BytesIO(pdf_buffer.getvalue()),
        mimetype='application/pdf',
        as_attachment=True,
        download_name='relatorio_disponibilidade.pdf'
    )

@app.route('/generate_qr/<int:classroom_id>')
def generate_qr(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    
    # Generate the full URL for the classroom
    classroom_url = request.url_root.rstrip('/') + url_for('classroom_detail', classroom_id=classroom_id)
    
    qr_buffer = generate_qr_code(classroom_url, classroom.name)
    
    return send_file(
        io.BytesIO(qr_buffer.getvalue()),
        mimetype='image/png',
        as_attachment=True,
        download_name=f'qr_sala_{classroom.name.replace(" ", "_")}.png'
    )

# Exportação para Excel
@app.route('/export_excel')
def export_excel():
    # Create workbook and worksheet
    wb = openpyxl.Workbook()
    
    # Sheet 1: Classrooms
    ws1 = wb.active
    ws1.title = "Salas de Aula"
    
    # Headers for classrooms
    headers1 = ['ID', 'Nome', 'Capacidade', 'Bloco', 'Andar', 'Tem Computadores', 'Softwares', 'Descrição']
    for col, header in enumerate(headers1, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        cell.font = Font(color='FFFFFF', bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data for classrooms
    classrooms = Classroom.query.all()
    for row, classroom in enumerate(classrooms, 2):
        ws1.cell(row=row, column=1, value=classroom.id)
        ws1.cell(row=row, column=2, value=classroom.name)
        ws1.cell(row=row, column=3, value=classroom.capacity)
        ws1.cell(row=row, column=4, value=classroom.block)
        ws1.cell(row=row, column=5, value=classroom.floor)
        ws1.cell(row=row, column=6, value='Sim' if classroom.has_computers else 'Não')
        ws1.cell(row=row, column=7, value=classroom.software)
        ws1.cell(row=row, column=8, value=classroom.description)
    
    # Auto-fit columns
    for column in ws1.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws1.column_dimensions[column_letter].width = adjusted_width
    
    # Sheet 2: Schedules
    ws2 = wb.create_sheet(title="Horários")
    
    # Headers for schedules
    headers2 = ['ID', 'Sala', 'Dia da Semana', 'Turno', 'Curso', 'Professor', 'Início', 'Fim', 'Ativo']
    for col, header in enumerate(headers2, 1):
        cell = ws2.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        cell.font = Font(color='FFFFFF', bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data for schedules
    schedules = Schedule.query.all()
    days = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    shifts = {'morning': 'Manhã', 'afternoon': 'Tarde', 'fullday': 'Integral', 'night': 'Noite'}
    
    for row, schedule in enumerate(schedules, 2):
        classroom = Classroom.query.get(schedule.classroom_id)
        ws2.cell(row=row, column=1, value=schedule.id)
        ws2.cell(row=row, column=2, value=classroom.name if classroom else 'N/A')
        ws2.cell(row=row, column=3, value=days[schedule.day_of_week])
        ws2.cell(row=row, column=4, value=shifts.get(schedule.shift, schedule.shift))
        ws2.cell(row=row, column=5, value=schedule.course_name)
        ws2.cell(row=row, column=6, value=schedule.instructor)
        ws2.cell(row=row, column=7, value=schedule.start_time)
        ws2.cell(row=row, column=8, value=schedule.end_time)
        ws2.cell(row=row, column=9, value='Sim' if schedule.is_active else 'Não')
    
    # Auto-fit columns
    for column in ws2.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws2.column_dimensions[column_letter].width = adjusted_width
    
    # Sheet 3: Statistics
    ws3 = wb.create_sheet(title="Estatísticas")
    
    # Statistics data
    total_classrooms = len(classrooms)
    total_schedules = len([s for s in schedules if s.is_active])
    total_slots = total_classrooms * 23  # 6 days * 4 shifts - 1 (no Saturday night)
    occupancy_rate = (total_schedules / total_slots * 100) if total_slots > 0 else 0
    
    stats_data = [
        ['Estatística', 'Valor'],
        ['Total de Salas', total_classrooms],
        ['Total de Horários Ativos', total_schedules],
        ['Total de Slots Possíveis', total_slots],
        ['Taxa de Ocupação (%)', f'{occupancy_rate:.1f}%'],
        ['Salas com Computadores', len([c for c in classrooms if c.has_computers])],
        ['Salas sem Computadores', len([c for c in classrooms if not c.has_computers])],
    ]
    
    for row, data in enumerate(stats_data, 1):
        for col, value in enumerate(data, 1):
            cell = ws3.cell(row=row, column=col, value=value)
            if row == 1:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
                cell.font = Font(color='FFFFFF', bold=True)
                cell.alignment = Alignment(horizontal='center')
    
    # Auto-fit columns
    for column in ws3.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 30)
        ws3.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'relatorio_senai_{timestamp}.xlsx'
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response

@app.route('/export_filtered_excel')
def export_filtered_excel():
    # Get the same filters as dashboard
    block_filter = request.args.get('block', '')
    floor_filter = request.args.get('floor', '')
    has_computers_filter = request.args.get('has_computers', '')
    capacity_filter = request.args.get('capacity', '')
    day_filter = request.args.get('day', '')
    shift_filter = request.args.get('shift', '')
    
    # Build filtered queries
    classroom_query = Classroom.query
    if block_filter:
        classroom_query = classroom_query.filter(Classroom.block == block_filter)
    if floor_filter:
        classroom_query = classroom_query.filter(Classroom.floor == int(floor_filter))
    if has_computers_filter:
        has_computers_bool = has_computers_filter.lower() == 'true'
        classroom_query = classroom_query.filter(Classroom.has_computers == has_computers_bool)
    if capacity_filter:
        capacity_ranges = {
            'small': (0, 20),
            'medium': (21, 35),
            'large': (36, 100)
        }
        if capacity_filter in capacity_ranges:
            min_cap, max_cap = capacity_ranges[capacity_filter]
            classroom_query = classroom_query.filter(
                Classroom.capacity >= min_cap,
                Classroom.capacity <= max_cap
            )
    
    filtered_classrooms = classroom_query.all()
    
    # Build schedule query with filters
    schedule_query = Schedule.query.filter_by(is_active=True)
    if day_filter:
        schedule_query = schedule_query.filter(Schedule.day_of_week == int(day_filter))
    if shift_filter:
        schedule_query = schedule_query.filter(Schedule.shift == shift_filter)
    
    filtered_schedules = schedule_query.all()
    
    # Create Excel file similar to export_excel but with filtered data
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "Salas Filtradas"
    
    # Headers
    headers1 = ['ID', 'Nome', 'Capacidade', 'Bloco', 'Andar', 'Tem Computadores', 'Softwares', 'Descrição']
    for col, header in enumerate(headers1, 1):
        cell = ws1.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color='366092', end_color='366092', fill_type='solid')
        cell.font = Font(color='FFFFFF', bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Data
    for row, classroom in enumerate(filtered_classrooms, 2):
        ws1.cell(row=row, column=1, value=classroom.id)
        ws1.cell(row=row, column=2, value=classroom.name)
        ws1.cell(row=row, column=3, value=classroom.capacity)
        ws1.cell(row=row, column=4, value=classroom.block)
        ws1.cell(row=row, column=5, value=classroom.floor)
        ws1.cell(row=row, column=6, value='Sim' if classroom.has_computers else 'Não')
        ws1.cell(row=row, column=7, value=classroom.software)
        ws1.cell(row=row, column=8, value=classroom.description)
    
    # Auto-fit columns
    for column in ws1.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws1.column_dimensions[column_letter].width = adjusted_width
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'relatorio_filtrado_{timestamp}.xlsx'
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    return response


@app.route('/delete_classroom/<int:classroom_id>', methods=['POST'])
def delete_classroom(classroom_id):
    if not session.get('admin_authenticated'):
        flash('Acesso negado. Faça login como administrador.', 'error')
        return redirect(url_for('auth'))
    
    classroom = Classroom.query.get_or_404(classroom_id)
    classroom_name = classroom.name
    
    # First delete all schedules associated with this classroom
    Schedule.query.filter_by(classroom_id=classroom_id).delete()
    
    # Then delete the classroom
    db.session.delete(classroom)
    db.session.commit()
    
    flash(f'Sala "{classroom_name}" foi excluída com sucesso!', 'success')
    return redirect(url_for('dashboard'))
