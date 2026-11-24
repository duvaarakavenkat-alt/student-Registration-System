
from flask import Flask, render_template, request
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Database connection
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create database table
def create_table():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT NOT NULL,
            department TEXT NOT NULL,
            course TEXT NOT NULL,
            address TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Student registration
@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    dob = request.form.get("dob", "")
    gender = request.form.get("gender", "")
    department = request.form.get("department", "")
    course = request.form.get("course", "").strip()
    address = request.form.get("address", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Required field validation
    if not all([name, email, phone, dob, gender,
                department, course, address, password,
                confirm_password]):
        return "Please fill all fields!"

    # Phone validation
    if not phone.isdigit() or len(phone) != 10:
        return "Enter a valid 10-digit phone number!"

    # Email validation
    if "@" not in email or "." not in email:
        return "Enter a valid email address!"

    # Password validation
    if len(password) < 8:
        return "Password must contain at least 8 characters!"

    if password != confirm_password:
        return "Passwords do not match!"

    # Password hashing
    hashed_password = generate_password_hash(password)

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO students
            (name, email, phone, dob, gender, department,
             course, address, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name, email, phone, dob, gender, department,
            course, address, hashed_password
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return "This email is already registered!"

    conn.close()

    return render_template(
        "result.html",
        name=name,
        email=email,
        phone=phone,
        department=department,
        course=course
    )


# Admin dashboard - view students
@app.route("/students")
def view_students():

    conn = get_db()

    students = conn.execute("""
        SELECT id, name, email, phone, department, course
        FROM students
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )


# Run application
if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5001)
