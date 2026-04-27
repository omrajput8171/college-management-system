import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'college-management-secret-key-2026'

DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                teacher_id INTEGER,
                student_id INTEGER,
                FOREIGN KEY (teacher_id) REFERENCES teachers (id),
                FOREIGN KEY (student_id) REFERENCES students (id)
            );
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                subject TEXT,
                contact TEXT,
                email TEXT
            );
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL,
                class TEXT NOT NULL,
                section TEXT NOT NULL,
                contact TEXT,
                email TEXT
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            );
            CREATE TABLE IF NOT EXISTS marks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                marks INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (id)
            );
            CREATE TABLE IF NOT EXISTS notices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            );
        """)
        db.commit()
        cursor = db.execute("SELECT * FROM users WHERE email = ?", ('admin@gmail.com',))
        if not cursor.fetchone():
            db.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)", ('Admin', 'admin@gmail.com', '12345', 'admin'))
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first', 'error')
                if role == 'admin':
                    return redirect(url_for('admin_login'))
                elif role == 'teacher':
                    return redirect(url_for('teacher_login'))
                elif role == 'student':
                    return redirect(url_for('student_login'))
                return redirect(url_for('home'))
            if role and session.get('role') != role:
                flash('Unauthorized access', 'error')
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = 'admin'", (email, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    db = get_db()
    total_students = db.execute("SELECT COUNT(*) as count FROM students").fetchone()['count']
    total_teachers = db.execute("SELECT COUNT(*) as count FROM teachers").fetchone()['count']
    total_classes = db.execute("SELECT COUNT(DISTINCT class) as count FROM students").fetchone()['count'] or 0
    notices = db.execute("SELECT * FROM notices ORDER BY date DESC LIMIT 5").fetchall()
    return render_template('admin_dashboard.html', total_students=total_students, total_teachers=total_teachers, total_classes=total_classes, notices=notices)

@app.route('/admin/teachers', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_teachers():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        subject = request.form.get('subject')
        contact = request.form.get('contact')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            cursor = db.execute("INSERT INTO teachers (name, subject, contact, email) VALUES (?, ?, ?, ?)", (name, subject, contact, email))
            teacher_id = cursor.lastrowid
            db.execute("INSERT INTO users (name, email, password, role, teacher_id) VALUES (?, ?, ?, ?, ?)", (name, email, password, 'teacher', teacher_id))
            db.commit()
            flash('Teacher added successfully with login credentials', 'success')
        except sqlite3.IntegrityError:
            flash('Email already exists', 'error')
        return redirect(url_for('admin_teachers'))
    teachers = db.execute("SELECT * FROM teachers ORDER BY id DESC").fetchall()
    return render_template('admin_teachers.html', teachers=teachers)

@app.route('/admin/teachers/edit/<int:id>', methods=['POST'])
@login_required(role='admin')
def admin_edit_teacher(id):
    db = get_db()
    name = request.form.get('name')
    subject = request.form.get('subject')
    contact = request.form.get('contact')
    email = request.form.get('email')
    try:
        db.execute("UPDATE teachers SET name = ?, subject = ?, contact = ?, email = ? WHERE id = ?", (name, subject, contact, email, id))
        db.commit()
        flash('Teacher updated successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Email already exists', 'error')
    return redirect(url_for('admin_teachers'))

@app.route('/admin/teachers/delete/<int:id>')
@login_required(role='admin')
def admin_delete_teacher(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE teacher_id = ?", (id,))
    db.execute("DELETE FROM teachers WHERE id = ?", (id,))
    db.commit()
    flash('Teacher deleted successfully', 'success')
    return redirect(url_for('admin_teachers'))

@app.route('/admin/students', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_students():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        roll_no = request.form.get('roll_no')
        class_name = request.form.get('class')
        section = request.form.get('section')
        contact = request.form.get('contact')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            cursor = db.execute("INSERT INTO students (name, roll_no, class, section, contact, email) VALUES (?, ?, ?, ?, ?, ?)", (name, roll_no, class_name, section, contact, email))
            student_id = cursor.lastrowid
            db.execute("INSERT INTO users (email, password, role, student_id) VALUES (?, ?, ?, ?)", (email, password, 'student', student_id))
            db.commit()
            flash('Student added successfully with login credentials', 'success')
        except sqlite3.IntegrityError:
            flash('Roll number or email already exists', 'error')
        return redirect(url_for('admin_students'))
    students = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return render_template('admin_students.html', students=students)

@app.route('/admin/students/edit/<int:id>', methods=['POST'])
@login_required(role='admin')
def admin_edit_student(id):
    db = get_db()
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')
    class_name = request.form.get('class')
    section = request.form.get('section')
    contact = request.form.get('contact')
    email = request.form.get('email')
    try:
        db.execute("UPDATE students SET name = ?, roll_no = ?, class = ?, section = ?, contact = ?, email = ? WHERE id = ?", (name, roll_no, class_name, section, contact, email, id))
        db.commit()
        flash('Student updated successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Roll number already exists', 'error')
    return redirect(url_for('admin_students'))

@app.route('/admin/students/delete/<int:id>')
@login_required(role='admin')
def admin_delete_student(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE student_id = ?", (id,))
    db.execute("DELETE FROM attendance WHERE student_id = ?", (id,))
    db.execute("DELETE FROM marks WHERE student_id = ?", (id,))
    db.execute("DELETE FROM students WHERE id = ?", (id,))
    db.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('admin_students'))

@app.route('/admin/notices', methods=['GET', 'POST'])
@login_required(role='admin')
def admin_notices():
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        notice_id = request.form.get('notice_id')
        date = datetime.now().strftime('%Y-%m-%d')
        if notice_id:
            db.execute("UPDATE notices SET title = ?, description = ? WHERE id = ?", (title, description, notice_id))
            flash('Notice updated successfully', 'success')
        else:
            db.execute("INSERT INTO notices (title, description, date) VALUES (?, ?, ?)", (title, description, date))
            flash('Notice added successfully', 'success')
        db.commit()
        return redirect(url_for('admin_notices'))
    notices = db.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    return render_template('admin_notices.html', notices=notices)

@app.route('/admin/notices/delete/<int:id>')
@login_required(role='admin')
def admin_delete_notice(id):
    db = get_db()
    db.execute("DELETE FROM notices WHERE id = ?", (id,))
    db.commit()
    flash('Notice deleted successfully', 'success')
    return redirect(url_for('admin_notices'))

@app.route('/teacher/login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = 'teacher'", (email, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['teacher_id'] = user['teacher_id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            flash('Login successful!', 'success')
            return redirect(url_for('teacher_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('teacher_login.html')

@app.route('/teacher/signup')
def teacher_signup():
    flash('Please contact admin to create your account', 'info')
    return redirect(url_for('teacher_login'))

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = 'student'", (email, password)).fetchone()
        if user:
            session['user_id'] = user['id']
            session['student_id'] = user['student_id']
            session['user_name'] = user['email']
            session['role'] = 'student'
            flash('Login successful!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('student_login.html')

@app.route('/student/signup')
def student_signup():
    flash('Please contact admin or teacher to create your account', 'info')
    return redirect(url_for('student_login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/teacher/dashboard')
@login_required(role='teacher')
def teacher_dashboard():
    db = get_db()
    total_students = db.execute("SELECT COUNT(*) as count FROM students").fetchone()['count']
    today = datetime.now().strftime('%Y-%m-%d')
    today_attendance = db.execute("SELECT COUNT(*) as count FROM attendance WHERE date = ?", (today,)).fetchone()['count']
    notices = db.execute("SELECT * FROM notices ORDER BY date DESC LIMIT 5").fetchall()
    return render_template('teacher_dashboard.html', total_students=total_students, today_attendance=today_attendance, notices=notices)

@app.route('/teacher/students', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_students():
    db = get_db()
    if request.method == 'POST':
        name = request.form.get('name')
        roll_no = request.form.get('roll_no')
        class_name = request.form.get('class')
        section = request.form.get('section')
        contact = request.form.get('contact')
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            cursor = db.execute("INSERT INTO students (name, roll_no, class, section, contact, email) VALUES (?, ?, ?, ?, ?, ?)", (name, roll_no, class_name, section, contact, email))
            student_id = cursor.lastrowid
            db.execute("INSERT INTO users (email, password, role, student_id) VALUES (?, ?, ?, ?)", (email, password, 'student', student_id))
            db.commit()
            flash('Student added successfully with login credentials', 'success')
        except sqlite3.IntegrityError:
            flash('Roll number or email already exists', 'error')
        return redirect(url_for('teacher_students'))
    students = db.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    return render_template('teacher_students.html', students=students)

@app.route('/teacher/students/edit/<int:id>', methods=['POST'])
@login_required(role='teacher')
def edit_student(id):
    db = get_db()
    name = request.form.get('name')
    roll_no = request.form.get('roll_no')
    class_name = request.form.get('class')
    section = request.form.get('section')
    contact = request.form.get('contact')
    email = request.form.get('email')
    try:
        db.execute("UPDATE students SET name = ?, roll_no = ?, class = ?, section = ?, contact = ?, email = ? WHERE id = ?", (name, roll_no, class_name, section, contact, email, id))
        db.commit()
        flash('Student updated successfully', 'success')
    except sqlite3.IntegrityError:
        flash('Roll number already exists', 'error')
    return redirect(url_for('teacher_students'))

@app.route('/teacher/students/delete/<int:id>')
@login_required(role='teacher')
def delete_student(id):
    db = get_db()
    db.execute("DELETE FROM users WHERE student_id = ?", (id,))
    db.execute("DELETE FROM attendance WHERE student_id = ?", (id,))
    db.execute("DELETE FROM marks WHERE student_id = ?", (id,))
    db.execute("DELETE FROM students WHERE id = ?", (id,))
    db.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('teacher_students'))

@app.route('/teacher/attendance', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_attendance():
    db = get_db()
    if request.method == 'POST':
        date = request.form.get('date')
        student_ids = request.form.getlist('student_id')
        statuses = request.form.getlist('status')
        for sid, status in zip(student_ids, statuses):
            existing = db.execute("SELECT * FROM attendance WHERE student_id = ? AND date = ?", (sid, date)).fetchone()
            if existing:
                db.execute("UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?", (status, sid, date))
            else:
                db.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (sid, date, status))
        db.commit()
        flash('Attendance marked successfully', 'success')
        return redirect(url_for('teacher_attendance', date=date))
    students = db.execute("SELECT * FROM students").fetchall()
    selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    attendance_records = db.execute("SELECT a.*, s.name, s.roll_no FROM attendance a JOIN students s ON a.student_id = s.id WHERE a.date = ?", (selected_date,)).fetchall()
    return render_template('teacher_attendance.html', students=students, attendance_records=attendance_records, selected_date=selected_date)

@app.route('/teacher/marks', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_marks():
    db = get_db()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject = request.form.get('subject')
        marks_val = request.form.get('marks')
        existing = db.execute("SELECT * FROM marks WHERE student_id = ? AND subject = ?", (student_id, subject)).fetchone()
        if existing:
            db.execute("UPDATE marks SET marks = ? WHERE student_id = ? AND subject = ?", (marks_val, student_id, subject))
        else:
            db.execute("INSERT INTO marks (student_id, subject, marks) VALUES (?, ?, ?)", (student_id, subject, marks_val))
        db.commit()
        flash('Marks saved successfully', 'success')
        return redirect(url_for('teacher_marks'))
    students = db.execute("SELECT * FROM students").fetchall()
    marks = db.execute("SELECT m.*, s.name, s.roll_no FROM marks m JOIN students s ON m.student_id = s.id ORDER BY m.id DESC").fetchall()
    return render_template('teacher_marks.html', students=students, marks=marks)

@app.route('/teacher/notices', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_notices():
    db = get_db()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        date = datetime.now().strftime('%Y-%m-%d')
        db.execute("INSERT INTO notices (title, description, date) VALUES (?, ?, ?)", (title, description, date))
        db.commit()
        flash('Notice added successfully', 'success')
        return redirect(url_for('teacher_notices'))
    notices = db.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    return render_template('teacher_notices.html', notices=notices)

@app.route('/teacher/notices/delete/<int:id>')
@login_required(role='teacher')
def delete_notice(id):
    db = get_db()
    db.execute("DELETE FROM notices WHERE id = ?", (id,))
    db.commit()
    flash('Notice deleted successfully', 'success')
    return redirect(url_for('teacher_notices'))

@app.route('/teacher/profile', methods=['GET', 'POST'])
@login_required(role='teacher')
def teacher_profile():
    db = get_db()
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if current_password and new_password:
            if user['password'] == current_password:
                db.execute("UPDATE users SET name = ?, email = ?, password = ? WHERE id = ?", (name, email, new_password, user_id))
                db.commit()
                session['user_name'] = name
                flash('Profile and password updated successfully', 'success')
            else:
                flash('Current password is incorrect', 'error')
                return redirect(url_for('teacher_profile'))
        else:
            try:
                db.execute("UPDATE users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
                db.commit()
                session['user_name'] = name
                flash('Profile updated successfully', 'success')
            except sqlite3.IntegrityError:
                flash('Email already exists', 'error')
                return redirect(url_for('teacher_profile'))
        return redirect(url_for('teacher_profile'))
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return render_template('teacher_profile.html', user=user)

@app.route('/student/dashboard')
@login_required(role='student')
def student_dashboard():
    db = get_db()
    student_id = session['student_id']
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    total_classes = db.execute("SELECT COUNT(*) as count FROM attendance WHERE student_id = ?", (student_id,)).fetchone()['count']
    present_classes = db.execute("SELECT COUNT(*) as count FROM attendance WHERE student_id = ? AND status = 'Present'", (student_id,)).fetchone()['count']
    attendance_percentage = round((present_classes / total_classes * 100), 2) if total_classes > 0 else 0
    marks = db.execute("SELECT * FROM marks WHERE student_id = ?", (student_id,)).fetchall()
    total_marks = sum(m['marks'] for m in marks) if marks else 0
    max_marks = len(marks) * 100 if marks else 0
    marks_percentage = round((total_marks / max_marks * 100), 2) if max_marks > 0 else 0
    notices = db.execute("SELECT * FROM notices ORDER BY date DESC LIMIT 3").fetchall()
    return render_template('student_dashboard.html', student=student, total_classes=total_classes, present_classes=present_classes, attendance_percentage=attendance_percentage, marks=marks, total_marks=total_marks, max_marks=max_marks, marks_percentage=marks_percentage, notices=notices)

@app.route('/student/attendance')
@login_required(role='student')
def student_attendance():
    db = get_db()
    student_id = session['student_id']
    attendance_records = db.execute("SELECT * FROM attendance WHERE student_id = ? ORDER BY date DESC", (student_id,)).fetchall()
    total_classes = len(attendance_records)
    present_classes = sum(1 for a in attendance_records if a['status'] == 'Present')
    attendance_percentage = round((present_classes / total_classes * 100), 2) if total_classes > 0 else 0
    return render_template('student_attendance.html', attendance_records=attendance_records, total_classes=total_classes, present_classes=present_classes, attendance_percentage=attendance_percentage)

@app.route('/student/marks')
@login_required(role='student')
def student_marks():
    db = get_db()
    student_id = session['student_id']
    marks = db.execute("SELECT * FROM marks WHERE student_id = ? ORDER BY subject", (student_id,)).fetchall()
    total_marks = sum(m['marks'] for m in marks) if marks else 0
    max_marks = len(marks) * 100 if marks else 0
    percentage = round((total_marks / max_marks * 100), 2) if max_marks > 0 else 0
    return render_template('student_marks.html', marks=marks, total_marks=total_marks, max_marks=max_marks, percentage=percentage)

@app.route('/student/notices')
@login_required(role='student')
def student_notices():
    db = get_db()
    notices = db.execute("SELECT * FROM notices ORDER BY date DESC").fetchall()
    return render_template('student_notices.html', notices=notices)

@app.route('/student/profile')
@login_required(role='student')
def student_profile():
    db = get_db()
    student_id = session['student_id']
    student = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return render_template('student_profile.html', student=student)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
