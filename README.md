# Online Exam System

A comprehensive, flask-based online examination web application that allows administrators to manage question banks and students to take exams for various subjects.

## Features

**For Administrators:**
- **Dashboard:** Overview of system activity.
- **Question Management:** Add, edit, and delete questions with ease. 
- **Support for Multiple Question Types:**
  - Multiple Choice Questions (MCQ)
  - Multiple Select Questions (Select all that apply)
  - Numerical Answers (with support for range-based answers, e.g., 40-45)
- **Rich Media Support:** Upload and attach images to questions to provide visual context.
- **Bulk Import:** Import questions quickly using a CSV file.
- **Results Tracking:** View student scores and exam submission dates.

**For Students:**
- **User Registration & Login:** Secure authentication system.
- **Student Dashboard:** View available exams across different subjects.
- **Interactive Exam Interface:**
  - Modern, responsive, glassmorphism UI.
  - Built-in exam timer with auto-submission.
  - Strict Anti-Cheat mechanisms (detects tab switching or minimizing the browser).
- **Instant Results & Review:** Get immediate scoring and review the correct answers and explanations after submission.

## Technologies Used

- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, Bootstrap 5.3, Bootstrap Icons
- **Styling:** Custom CSS with Glassmorphism effects and modern fonts (Outfit).

## Project Structure

```
online-exam-system/
│
├── app.py                  # Main Flask application and routing logic
├── database.sql            # Database schema definitions
├── requirements.txt        # Python dependencies
│
├── static/                 # Static assets
│   ├── style.css           # Custom styling
│   └── uploads/            # Directory for uploaded question images
│
├── templates/              # HTML templates (Jinja2)
│   ├── admin.html          # Admin dashboard and question management
│   ├── dashboard.html      # Student dashboard
│   ├── exam.html           # Exam taking interface
│   ├── login.html          # Login page
│   ├── register.html       # Student registration page
│   └── result.html         # Exam results and review page
│
├── migrate.py              # Database migration scripts
└── migrate_image.py        # Scripts to update database schema for images
```

## Setup & Installation

1. **Clone the repository.**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Configuration:**
   - Create a MySQL database (e.g., `online_exam`).
   - Import the schema from `database.sql`.
   - Update the MySQL connection details in `app.py`:
     ```python
     app.config['MYSQL_HOST'] = 'localhost'
     app.config['MYSQL_USER'] = 'root'
     app.config['MYSQL_PASSWORD'] = 'your_mysql_password'
     app.config['MYSQL_DB'] = 'online_exam'
     app.config['MYSQL_PORT'] = 3307  # Update port if necessary
     ```
4. **Run the application:**
   ```bash
   python app.py
   ```
5. **Access the application:**
   Open a web browser and navigate to `http://localhost:5000`.

## Default Access (Example)
- **Admin Login:** Requires an account with the role set to `admin` in the database.
- **Student Login:** Can register directly via the `/register` route.
