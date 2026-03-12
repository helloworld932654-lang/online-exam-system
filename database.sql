CREATE DATABASE IF NOT EXISTS online_exam;
USE online_exam;

-- Users table (students and admins)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'admin') DEFAULT 'student'
);

-- Questions table
CREATE TABLE questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject VARCHAR(100) DEFAULT 'General',
    type VARCHAR(20) DEFAULT 'mcq',
    question TEXT NOT NULL,
    option1 VARCHAR(255) DEFAULT '',
    option2 VARCHAR(255) DEFAULT '',
    option3 VARCHAR(255) DEFAULT '',
    option4 VARCHAR(255) DEFAULT '',
    correct_option VARCHAR(255) NOT NULL,
    answer_explanation TEXT,
    image_path VARCHAR(255)
);

-- Results table
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    exam_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert default admin
INSERT INTO users (name, email, password, role) VALUES ('Admin', 'admin@exam.com', 'admin123', 'admin');

-- Insert sample questions
INSERT INTO questions (subject, type, question, option1, option2, option3, option4, correct_option, answer_explanation, image_path) VALUES
('General', 'mcq', 'What does CPU stand for?', 'Central Processing Unit', 'Central Program Utility', 'Computer Personal Unit', 'Central Processor Unifier', '1', NULL, NULL),
('General', 'mcq', 'Which is not an operating system?', 'Windows', 'Linux', 'Oracle', 'macOS', '3', NULL, NULL),
('General', 'mcq', 'RAM stands for?', 'Random Access Memory', 'Read Access Memory', 'Run Access Memory', 'Random Allowed Memory', '1', NULL, NULL),
('General', 'mcq', 'Which language is used for web development?', 'Python', 'HTML', 'C++', 'Assembly', '2', NULL, NULL),
('General', 'mcq', 'What is the full form of HTTP?', 'HyperText Transfer Protocol', 'HyperText Test Protocol', 'Hyper Transfer Text Protocol', 'High Text Transfer Protocol', '1', NULL, NULL);
