from flask import Flask, render_template, request, redirect, url_for, session, flash
import psycopg2
import random
import csv
import io
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["DEBUG"] = True
app.secret_key = 'your_secret_key_here'  # Change this in production

# ============ MySQL Configuration ============
DB_HOST = "db.cnptajqxlhqkeyxbsuqk.supabase.co"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "Nutan@932654"
DB_PORT = 5432
# ============ Uploads Configuration ============
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'questions')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

# ============ HOME / LOGIN ============
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login for both students and admins"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        cur.close()
        db.close()

        if user:
            # Store user info in session
            session['user_id'] = user[0]
            session['name'] = user[1]
            session['role'] = user[4]

            if user[4] == 'admin':
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')

    return render_template('login.html')

# ============ REGISTER ============
@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new student registration"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, 'student')",
                        (name, email, password))
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError:
            flash('Email already exists!', 'danger')
        finally:
            cur.close()
            db.close()

    return render_template('register.html')

# ============ STUDENT DASHBOARD ============
@app.route('/dashboard')
def dashboard():
    """Student dashboard - shows exam options and past results"""
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    
    # Get user results
    cur.execute("SELECT score, exam_date, subject FROM results WHERE user_id=%s ORDER BY exam_date DESC", (session['user_id'],))
    results = cur.fetchall()
    
    # Get available subjects
    cur.execute("SELECT DISTINCT subject FROM questions")
    subjects = [row[0] for row in cur.fetchall()]
    
    cur.close()
    db.close()

    return render_template('dashboard.html', name=session['name'], results=results, subjects=subjects)

# ============ EXAM ROUTE (Grading update) ============
@app.route('/exam/<subject>', methods=['GET', 'POST'])
def exam(subject):
    """Display exam questions for a specific subject and handle submission"""
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    if request.method == 'POST':
        # Calculate score
        cur.execute("SELECT id, correct_option, type, question, answer_explanation, image_path FROM questions WHERE subject=%s", (subject,))
        questions = cur.fetchall()
        score = 0
        
        # We will build a list of dictionaries to pass to the result page for review
        review_data = []

        for q in questions:
            q_id = q[0]
            correct_ans = str(q[1]).strip()
            q_type = q[2]
            question_text = q[3]
            explanation = q[4]
            image_path = q[5] if len(q) > 5 else None
            
            is_correct = False
            user_answer = ""
            
            if q_type == 'mcq':
                selected = request.form.get(f'question_{q_id}')
                user_answer = selected if selected else "No Answer"
                if selected and selected.strip() == correct_ans:
                    score += 1
                    is_correct = True
            elif q_type == 'multiselect':
                # Grab all checked checkboxes
                selected_list = request.form.getlist(f'question_{q_id}')
                user_answer = ",".join(selected_list) if selected_list else "No Answer"
                if selected_list:
                    valid_selected = [x.strip() for x in selected_list if x.strip()]
                    valid_correct = [x.strip() for x in correct_ans.split(",") if x.strip()]
                    selected_joined = ",".join(sorted(valid_selected))
                    correct_joined = ",".join(sorted(valid_correct))
                    if selected_joined == correct_joined:
                        score += 1
                        is_correct = True
            elif q_type == 'numerical':
                selected = request.form.get(f'question_{q_id}')
                user_answer = selected if selected else "No Answer"
                if selected:
                    try:
                        sel_val = float(selected.strip())
                        # Check if correct_ans is a range
                        if '-' in correct_ans:
                            min_val, max_val = map(float, correct_ans.split('-'))
                            if min_val <= sel_val <= max_val:
                                score += 1
                                is_correct = True
                        else:
                            if sel_val == float(correct_ans):
                                score += 1
                                is_correct = True
                    except ValueError:
                        pass
            
            # Store data for the review page
            review_data.append({
                'question': question_text,
                'user_answer': user_answer,
                'correct_answer': correct_ans,
                'is_correct': is_correct,
                'explanation': explanation,
                'image_path': image_path
            })

        # Save result
        cur.execute("INSERT INTO results (user_id, score, subject) VALUES (%s, %s, %s)", (session['user_id'], score, subject))
        db.commit()

        # Simulate Sending Email
        try:
            cur.execute("SELECT email FROM users WHERE id=%s", (session['user_id'],))
            user_data = cur.fetchone()
            if user_data:
                student_email = user_data[0]
                print("\n" + "="*40)
                print(f"📧 SIMULATED EMAIL SENT TO: {student_email}")
                print(f"Subject: Your {subject} Exam Results - Online Exam System")
                print(f"Body: Hello {session.get('name', 'Student')}, you just completed your {subject} exam!")
                print(f"Your score is: {score} out of {len(questions)}")
                print("="*40 + "\n")
        except Exception as e:
            print("Failed to simulate email:", str(e))

        cur.close()
        db.close()
        
        return render_template('result.html', score=score, total=len(questions), name=session['name'], subject=subject, review_data=review_data)

    # GET - show exam
    cur.execute("SELECT * FROM questions WHERE subject=%s", (subject,))
    questions = cur.fetchall()
    cur.close()
    db.close()
    
    # Convert tuple to list to allow shuffling
    questions = list(questions)
    random.shuffle(questions)

    return render_template('exam.html', questions=questions, subject=subject)

# ============ RESULT ============
@app.route('/result')
def result():
    """Display exam result"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    score = request.args.get('score', 0)
    total = request.args.get('total', 0)
    return render_template('result.html', score=score, total=total, name=session['name'])

# ============ ADMIN PANEL ============
@app.route('/admin')
def admin():
    """Admin dashboard - manage questions and view results"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()

    # Get all questions
    cur.execute("SELECT * FROM questions")
    questions = cur.fetchall()

    # Get all student results with names
    cur.execute("""
        SELECT u.name, u.email, r.score, r.exam_date
        FROM results r JOIN users u ON r.user_id = u.id
        ORDER BY r.exam_date DESC
    """)
    results = cur.fetchall()

    cur.close()
    db.close()

    return render_template('admin.html', questions=questions, results=results)

# ============ ADD QUESTION ============
@app.route('/add_question', methods=['POST'])
def add_question():
    """Admin: Add a new question"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    q_type = request.form.get('type', 'mcq')
    subject = request.form.get('subject', 'General').strip()
    explanation = request.form.get('answer_explanation', '')
    
    # Handle checkboxes vs single values for correct answers
    if q_type == 'multiselect':
        correct_ans = ",".join(request.form.getlist('correct_option'))
    else:
        correct_ans = request.form.get('correct_option')

    # Handle Image Upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # Create a unique filename
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            # Store relative path for frontend access
            image_path = f"uploads/questions/{unique_filename}"

    db = get_db()
    cur = db.cursor()
    cur.execute("""INSERT INTO questions (type, subject, question, option1, option2, option3, option4, correct_option, answer_explanation, image_path)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (q_type, subject, request.form.get('question', ''), request.form.get('option1', ''), 
                 request.form.get('option2', ''), request.form.get('option3', ''), 
                 request.form.get('option4', ''), str(correct_ans), explanation, image_path))
    db.commit()
    cur.close()
    db.close()

    flash('Question added successfully!', 'success')
    return redirect(url_for('admin'))

# ============ EDIT QUESTION ============
@app.route('/edit_question/<int:id>', methods=['POST'])
def edit_question(id):
    """Admin: Edit an existing question"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    q_type = request.form.get('type', 'mcq')
    subject = request.form.get('subject', 'General').strip()
    explanation = request.form.get('answer_explanation', '')
    
    if q_type == 'multiselect':
        correct_ans = ",".join(request.form.getlist('correct_option'))
    else:
        correct_ans = request.form.get('correct_option')

    # Handle Image Upload
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            image_path = f"uploads/questions/{unique_filename}"

    db = get_db()
    cur = db.cursor()
    
    if image_path:
        cur.execute("""UPDATE questions SET type=%s, subject=%s, question=%s, option1=%s, option2=%s, option3=%s, option4=%s, correct_option=%s, answer_explanation=%s, image_path=%s
                       WHERE id=%s""",
                    (q_type, subject, request.form.get('question', ''), request.form.get('option1', ''), 
                     request.form.get('option2', ''), request.form.get('option3', ''), 
                     request.form.get('option4', ''), str(correct_ans), explanation, image_path, id))
    else:
        # If no new image, leave existing image as is
        cur.execute("""UPDATE questions SET type=%s, subject=%s, question=%s, option1=%s, option2=%s, option3=%s, option4=%s, correct_option=%s, answer_explanation=%s
                       WHERE id=%s""",
                    (q_type, subject, request.form.get('question', ''), request.form.get('option1', ''), 
                     request.form.get('option2', ''), request.form.get('option3', ''), 
                     request.form.get('option4', ''), str(correct_ans), explanation, id))

    db.commit()
    cur.close()
    db.close()

    flash('Question updated!', 'success')
    return redirect(url_for('admin'))

# ============ DELETE QUESTION ============
@app.route('/delete_question/<int:id>')
def delete_question(id):
    """Admin: Delete a question"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM questions WHERE id=%s", (id,))
    db.commit()
    cur.close()
    db.close()

    flash('Question deleted!', 'success')
    return redirect(url_for('admin'))

# ============ IMPORT QUESTIONS ============
@app.route('/import_questions', methods=['POST'])
def import_questions():
    """Admin: Import questions from CSV"""
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('admin'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('admin'))

    if file and file.filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        
        db = get_db()
        cur = db.cursor()
        
        try:
            # Skip header if it exists
            header = next(csv_input, None)
            
            count = 0
            for row in csv_input:
                if len(row) >= 6:
                    cur.execute("""INSERT INTO questions (question, option1, option2, option3, option4, correct_option)
                                   VALUES (%s, %s, %s, %s, %s, %s)""",
                                (row[0], row[1], row[2], row[3], row[4], row[5]))
                    count += 1
            
            db.commit()
            flash(f'Successfully imported {count} questions!', 'success')
        except Exception as e:
            flash(f'Error importing from CSV: {str(e)}', 'danger')
        finally:
            cur.close()
            db.close()
    else:
        flash('Allowed file type is CSV only', 'danger')
        
    return redirect(url_for('admin'))

# ============ LOGOUT ============
@app.route('/logout')
def logout():
    """Clear session and logout"""
    session.clear()
    return redirect(url_for('login'))

# ============ RUN APP ============
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
