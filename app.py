from flask import Flask, render_template, request, session, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from functools import wraps
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    problems = db.relationship('Problem', backref='student', lazy=True)
    comments = db.relationship('Comment', backref='student', lazy=True)
    upvotes = db.relationship('Upvote', backref='student', lazy=True)

class HOD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    comments = db.relationship('Comment', backref='hod', lazy=True)

class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    priority = db.Column(db.String(50), nullable=False, default='Medium')
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comments = db.relationship('Comment', backref='problem', lazy=True, cascade="all, delete-orphan")
    upvotes = db.relationship('Upvote', backref='problem', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    hod_id = db.Column(db.Integer, db.ForeignKey('hod.id'), nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Upvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(db.Integer, db.ForeignKey('problem.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

# Login Decorators
def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated_function

def hod_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'hod_id' not in session:
            return redirect(url_for('hod_login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'pdf'}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email).first()

        if student is None:
            return render_template('student_login.html', error='No account found with that email.')

        if check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            return redirect(url_for('student_dashboard'))
        else:
            return render_template('student_login.html', error='Incorrect password.')

    return render_template('student_login.html')

@app.route('/student-signup', methods=['GET', 'POST'])
def student_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        year = request.form['year']
        password = request.form['password']

        existing_student = Student.query.filter_by(email=email).first()
        if existing_student:
            return render_template('student_signup.html', error='An account with that email already exists.')

        hashed_password = generate_password_hash(password)
        new_student = Student(
            name=name,
            email=email,
            department=department,
            year=year,
            password=hashed_password
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('student_login'))

    return render_template('student_signup.html')

@app.route('/hod-login', methods=['GET', 'POST'])
def hod_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hod = HOD.query.filter_by(username=username).first()

        if hod is None:
            return render_template('hod_login.html', error='No account found with that username.')

        if check_password_hash(hod.password, password):
            session['hod_id'] = hod.id
            session['hod_username'] = hod.username
            return redirect(url_for('hod_dashboard'))
        else:
            return render_template('hod_login.html', error='Incorrect password.')

    return render_template('hod_login.html')

@app.route('/student-dashboard')
@student_login_required
def student_dashboard():
    return render_template('student_dashboard.html', student_name=session['student_name'])

@app.route('/submit-problem', methods=['GET', 'POST'])
@student_login_required
def submit_problem():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        description = request.form['description']
        priority = request.form.get('priority', 'Medium')
        is_public = 'is_public' in request.form
        
        filename = None
        if 'attachment' in request.files:
            file = request.files['attachment']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        problem = Problem(
            student_id=session['student_id'],
            title=title,
            category=category,
            description=description,
            attachment=filename,
            priority=priority,
            is_public=is_public
        )
        db.session.add(problem)
        db.session.commit()

        flash('Problem submitted successfully!', 'success')
        return redirect(url_for('my_problems'))

    return render_template('submit_problem.html')

@app.route('/my-problems')
@student_login_required
def my_problems():
    problems = Problem.query.filter_by(student_id=session['student_id']).order_by(Problem.created_at.desc()).all()
    return render_template('my_problems.html', problems=problems)

@app.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
@student_login_required
def problem_details(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    if problem.student_id != session['student_id'] and not problem.is_public:
        return "Unauthorized", 403

    if request.method == 'POST':
        body = request.form['body']
        comment = Comment(problem_id=problem.id, student_id=session['student_id'], body=body)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('problem_details', problem_id=problem.id))
        
    comments = Comment.query.filter_by(problem_id=problem.id).order_by(Comment.created_at.asc()).all()
    return render_template('problem_details.html', problem=problem, comments=comments)

@app.route('/public-board')
@student_login_required
def public_board():
    problems = Problem.query.filter_by(is_public=True).order_by(Problem.created_at.desc()).all()
    return render_template('public_board.html', problems=problems)

@app.route('/upvote/<int:problem_id>', methods=['POST'])
@student_login_required
def upvote(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    if not problem.is_public:
        return "Cannot upvote private problem", 400
        
    existing_upvote = Upvote.query.filter_by(problem_id=problem.id, student_id=session['student_id']).first()
    if existing_upvote:
        db.session.delete(existing_upvote)
    else:
        new_upvote = Upvote(problem_id=problem.id, student_id=session['student_id'])
        db.session.add(new_upvote)
    
    db.session.commit()
    return redirect(request.referrer or url_for('public_board'))

@app.route('/hod-dashboard')
@hod_login_required
def hod_dashboard():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')

    query = Problem.query

    if search:
        query = query.filter(Problem.title.contains(search) | Problem.description.contains(search))
    if status:
        query = query.filter(Problem.status == status)
    if category:
        query = query.filter(Problem.category == category)
    if priority:
        query = query.filter(Problem.priority == priority)

    problems_pagination = query.order_by(Problem.created_at.desc()).paginate(page=page, per_page=10)
    
    total_count = Problem.query.count()
    pending_count = Problem.query.filter_by(status='Pending').count()
    in_progress_count = Problem.query.filter_by(status='In Progress').count()
    solved_count = Problem.query.filter_by(status='Solved').count()

    return render_template(
        'hod_dashboard.html',
        hod_username=session['hod_username'],
        problems_pagination=problems_pagination,
        total_count=total_count,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        solved_count=solved_count,
        now=datetime.utcnow()
    )

@app.route('/hod-problem/<int:problem_id>', methods=['GET', 'POST'])
@hod_login_required
def hod_problem_details(problem_id):
    problem = Problem.query.get_or_404(problem_id)

    if request.method == 'POST':
        if 'status' in request.form:
            problem.status = request.form['status']
            problem.updated_at = datetime.utcnow()
            flash('Status updated successfully.', 'success')
        if 'body' in request.form:
            body = request.form['body']
            if body.strip():
                comment = Comment(problem_id=problem.id, hod_id=session['hod_id'], body=body)
                db.session.add(comment)
                flash('Reply sent successfully.', 'success')
        db.session.commit()
        return redirect(url_for('hod_problem_details', problem_id=problem.id))

    comments = Comment.query.filter_by(problem_id=problem.id).order_by(Comment.created_at.asc()).all()
    return render_template('hod_problem_details.html', problem=problem, comments=comments)

@app.route('/hod-update-status/<int:problem_id>', methods=['POST'])
@hod_login_required
def hod_update_status(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    if 'status' in request.form:
        problem.status = request.form['status']
        problem.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Status updated to {problem.status}.', 'success')
    return redirect(request.referrer or url_for('hod_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)