from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
import logging
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from r1 import extract_resume_text, analyze_resume, preprocess_text, extract_skills_from_description, roadmap_suggestions, generate_html_report
import sqlite3
from functools import wraps
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   filename='app.log')

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MIME_TYPES = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png'
}

def init_db():
    with sqlite3.connect('resume_parser.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def fetch_job_openings_by_description(description):
    search_query = urllib.parse.quote(description)
    job_openings = {
        "Indeed": f"https://www.indeed.com/jobs?q={search_query}",
        "Glassdoor": f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_query}",
        "LinkedIn": f"https://www.linkedin.com/jobs/search/?keywords={search_query}"
    }
    return job_openings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with sqlite3.connect('resume_parser.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                             (username, generate_password_hash(password)))
                conn.commit()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
        except Exception as e:
            flash('Registration failed!', 'danger')
            logging.error(f"Registration error: {str(e)}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            with sqlite3.connect('resume_parser.db') as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT id, password FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user[1], password):
                    session['user_id'] = user[0]
                    session['username'] = username
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid username or password', 'danger')
        except Exception as e:
            flash('Login failed!', 'danger')
            logging.error(f"Login error: {str(e)}")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/analyze', methods=['POST'])
@login_required
def analyze():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    try:
        resume_text = extract_resume_text(file_path)
        if "Error" in resume_text:
            logging.error(f"Resume extraction error: {resume_text}")
            return jsonify({'error': resume_text}), 400
        
        score, structured, extracted_skills, job_recommendations, llm_analysis = analyze_resume(resume_text)
        
        job_description = request.form.get('job_description', '')
        job_openings_by_description = fetch_job_openings_by_description(job_description)
        skills_from_description = extract_skills_from_description(job_description)
        roadmap_by_description = roadmap_suggestions(skills_from_description)
        
        html_report = generate_html_report(score, structured, extracted_skills, job_recommendations, llm_analysis, job_openings_by_description, roadmap_by_description)
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], "resume_analysis_report.html")
        with open(report_path, "w", encoding="utf-8") as report_file:
            report_file.write(html_report)
        
        return jsonify({'message': 'Analysis complete', 'report_path': report_path}), 200
    except Exception as e:
        logging.error(f"Analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)