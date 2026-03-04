from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# -----------------------------
# ADMIN FIXED CREDENTIALS
# -----------------------------
ADMIN_EMAIL = "admin@123"
ADMIN_PASSWORD = "admin123"

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # CONTENT TABLE (NEW)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        title TEXT,
        content_type TEXT,
        content_link TEXT
    )
""")

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# LOGIN ROUTE
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        # ADMIN LOGIN
        if role == "admin":
            if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
                return redirect("/admin_dashboard")
            else:
                return "Invalid Admin Credentials"

        # STUDENT LOGIN
        elif role == "student":
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            cur.execute(
                "SELECT * FROM users WHERE email=? AND password=? AND role='student'",
                (email, password)
            )

            user = cur.fetchone()
            conn.close()

            if user:
                return redirect("/student_dashboard")
            else:
                return "Account not found. Please register first."

    return render_template("login.html")

# -----------------------------
# REGISTER ROUTE
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, password, "student")
            )
            conn.commit()
        except:
            conn.close()
            return "Email already exists!"

        conn.close()
        return redirect("/")

    return render_template("register.html")

# -----------------------------
# DASHBOARDS
# -----------------------------
@app.route("/student_dashboard")
def student_dashboard():
    return render_template("student_dashboard.html")

@app.route("/admin_dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

# -----------------------------
# VIEW STUDENTS (ADMIN)
# -----------------------------
@app.route("/manage_content")
def manage_content():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM content")
    contents = cur.fetchall()

    conn.close()
    return render_template("manage_content.html", contents=contents)


# -----------------------------
# DELETE CONTENT
# -----------------------------
@app.route("/delete_content/<int:id>")
def delete_content(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM content WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/manage_content")


# -----------------------------
# EDIT CONTENT
# -----------------------------
@app.route("/edit_content/<int:id>", methods=["GET", "POST"])
def edit_content(id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    if request.method == "POST":
        category = request.form["category"]
        title = request.form["title"]
        description = request.form["description"]

        cur.execute("""
            UPDATE content
            SET category=?, title=?, description=?
            WHERE id=?
        """, (category, title, description, id))

        conn.commit()
        conn.close()
        return redirect("/manage_content")

    cur.execute("SELECT * FROM content WHERE id=?", (id,))
    content = cur.fetchone()
    conn.close()

    return render_template("edit_content.html", content=content)

@app.route("/view_students")
def view_students():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("SELECT name, email FROM users WHERE role='student'")
    students = cur.fetchall()

    conn.close()

    return render_template("view_students.html", students=students)
# -----------------------------
# SELECT CATEGORY PAGE (ADMIN)
# -----------------------------
@app.route("/select_category")
def select_category():
    return render_template("select_category.html")
# -----------------------------
# ADMIN ADD CONTENT
# -----------------------------

@app.route("/add_content/<category>", methods=["GET", "POST"])
def add_content(category):
    if request.method == "POST":
        title = request.form["title"]
        content_type = request.form["content_type"]
        content_link = request.form["content_link"]

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO content (category, title, content_type, content_link)
            VALUES (?, ?, ?, ?)
        """, (category, title, content_type, content_link))

        conn.commit()
        conn.close()

        return redirect("/admin_dashboard")

    return render_template("add_content.html", category=category)
# -----------------------------
# STUDENT VIEW CONTENT CATEGORY-WISE
# -----------------------------
@app.route("/content/<category>")
def view_content(category):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row 
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM content WHERE category=?",
        (category,)
    )

    contents = cur.fetchall()
    conn.close()

    return render_template("view_content.html",
                           contents=contents,
                           category=category)

# -----------------------------
# OTHER PAGES
# -----------------------------
@app.route('/technical')
def technical():
    return render_template('technical.html')

@app.route("/year_roadmap")
def year_roadmap():
    return render_template("roadmap.html")

@app.route("/operating_system")
def operating_system():
    return render_template("os.html")

@app.route("/database")
def database():
    return render_template("dbms.html")

@app.route("/coding_platforms")
def coding_platforms():
    return render_template("coding_platforms.html")

@app.route("/aptitude/<section>")
@app.route("/aptitude/<section>/<content_type>")
def aptitude(section, content_type=None):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if content_type:
        cur.execute(
            "SELECT * FROM content WHERE LOWER(category)=? AND LOWER(title)=? AND LOWER(content_type)=?",
            ("aptitude", section.lower(), content_type.lower())
        )
    else:
        cur.execute(
            "SELECT * FROM content WHERE LOWER(category)=? AND LOWER(title)=?",
            ("aptitude", section.lower())
        )

    contents = cur.fetchall()
    conn.close()

    return render_template("aptitude.html",
                           contents=contents,
                           selected_section=section,
                           selected_type=content_type)
@app.route('/interview-skills')
def interview_skills():
    return render_template('interview_skills.html')

@app.route('/online_profile')
def online_profile():
    return render_template('online_profile.html')

@app.route('/resume_form')
def resume_form():
    return render_template('resume_form.html')

# -----------------------------
# GENERATE RESUME
# -----------------------------
@app.route('/generate_resume', methods=["POST"])
def generate_resume():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    skills = request.form['skills']
    education = request.form['education']
    experience = request.form['experience']

    improved_skills = skills.upper()
    improved_experience = "• " + experience.replace(",", "\n• ")

    return render_template('resume_output.html',
                           name=name,
                           email=email,
                           phone=phone,
                           skills=improved_skills,
                           education=education,
                           experience=improved_experience)

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)