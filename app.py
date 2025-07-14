
from flask import Flask, render_template, session,flash

from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect,url_for
from datetime import datetime
from employee_routes import employee_bp
from db import connect_db
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()
app=Flask(__name__)
app.secret_key=os.getenv('SECRET_KEY')

@app.route("/")
def home():
    return render_template('home.html',name="Atansh")
@app.route("/login",methods=["GET"])
def login_form():
    return render_template(template_name_or_list='login.html')
@app.route("/login",methods=["POST"])
def login_submit():
    username=request.form["email"]
    password=request.form["password"]
    db=connect_db()
    cursor=db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM employees WHERE email=%s',(username,))
    user=cursor.fetchone()
    cursor.close()
    db.close()
    if user and check_password_hash(user['password'],password):
        session['id']=user['id']
        session['username']=user['name']
        session['email'] = user['email']
        session['role']=user['role']
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))  # this is /employees
        else:
            return redirect(url_for('employee.employee_dashboard'))  # you'll create this

    return  render_template('login.html', error="Invalid email or password")
@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Access Denied", 403
    return render_template("admin_dashboard.html", name=session.get("username"))

@app.route("/add_employee", methods=["GET", "POST"])
def add_employee():
    if session.get("role") != "admin":
        return "Access Denied", 403

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        role = request.form["role"]
        password = generate_password_hash(request.form["password"])
        base_salary = request.form.get("base_salary") or 0  # default if empty
        # ✅ Get current month and year
        now = datetime.now()
        current_month = now.strftime("%B")  # e.g., 'July'
        current_year = now.year             # e.g., 2025
        # Save uploaded photo
        photo = request.files["photo"]
        faces_dir = os.path.join("static", "faces")
        filename = secure_filename(email + ".jpg")
        photo_path = os.path.join(faces_dir, filename)
        photo.save(photo_path)

        db = connect_db()
        cursor = db.cursor()

        # 1. Insert into employees table
        cursor.execute("""
            INSERT INTO employees (name, email, phone, role, password, photo_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, phone, role, password, filename))

        employee_id = cursor.lastrowid  # get auto-increment ID

        # 2. Optionally, insert default payroll row
        cursor.execute("""
            INSERT INTO payroll (employee_id, month, year, base_salary, bonus, deductions, net_salary)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (employee_id, current_month, current_year, base_salary, 0.00, 0.00, base_salary))  # net = base

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("admin_dashboard"))

    return render_template("add_employee.html")

@app.route("/delete_employee")
def delete_employee_page():
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees where role = 'employee'")
    employees = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("delete_employee.html", employees=employees)
@app.route("/delete_employee_confirm/<int:emp_id>", methods=["POST"])
def delete_employee_confirm(emp_id):
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor()

    # Delete from related tables
    cursor.execute("DELETE FROM attendance WHERE employee_id = %s", (emp_id,))
    cursor.execute("DELETE FROM leave_requests WHERE employee_id = %s", (emp_id,))
    cursor.execute("DELETE FROM payroll WHERE employee_id = %s", (emp_id,))

    # Delete from employees
    cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))

    db.commit()
    cursor.close()
    db.close()
    flash("✅ Employee deleted successfully.")
    return redirect(url_for("delete_employee_page"))


@app.route("/attendance")
def view_attendance():
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.id, a.date, a.status, e.name, e.email
        FROM attendance a
        JOIN employees e ON a.employee_id = e.id
        ORDER BY a.date DESC
    """)
    records = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("attendance.html", records=records)


@app.route("/leave_requests")
def view_leave_requests():
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT lr.*, e.name 
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        ORDER BY lr.status = 'Pending' DESC, lr.id DESC
    """)
    requests = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("leave_requests.html", requests=requests)

@app.route("/leave_requests/<int:req_id>/<action>", methods=["POST"])
def handle_leave_request(req_id, action):
    if session.get("role") != "admin":
        return "Access Denied", 403

    if action not in ["approve", "reject"]:
        return "Invalid action", 400

    new_status = "Approved" if action == "approve" else "Rejected"

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("UPDATE leave_requests SET status = %s WHERE id = %s", (new_status, req_id))
    db.commit()
    cursor.close()
    db.close()

    flash(f"Leave request {new_status.lower()} successfully.")
    return redirect(url_for("view_leave_requests"))

@app.route("/edit_employee")
def edit_employee_list():
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees WHERE role = 'employee'")
    employees = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template("edit_employee_list.html", employees=employees)
@app.route("/edit_employee/<int:emp_id>")
def edit_employee_form(emp_id):
    if session.get("role") != "admin":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM employees WHERE id = %s", (emp_id,))
    emp = cursor.fetchone()

    # Latest payroll record for this employee
    cursor.execute("""
        SELECT * FROM payroll 
        WHERE employee_id = %s 
        ORDER BY year DESC, 
                 FIELD(month, 'January','February','March','April','May','June','July','August','September','October','November','December') DESC 
        LIMIT 1
    """, (emp_id,))
    payroll = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("edit_employee_form.html", emp=emp, payroll=payroll)

@app.route("/edit_employee/<int:emp_id>", methods=["POST"])
def edit_employee_submit(emp_id):
    if session.get("role") != "admin":
        return "Access Denied", 403

    # Employee data
    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]
    role = request.form["role"]

    # Payroll data
    payroll_id = request.form["payroll_id"]
    base_salary = float(request.form["base_salary"])
    bonus = float(request.form["bonus"])
    deductions = float(request.form["deductions"])
    net_salary = base_salary + bonus - deductions

    db = connect_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE employees 
        SET name=%s, email=%s, phone=%s, role=%s 
        WHERE id=%s
    """, (name, email, phone, role, emp_id))

    cursor.execute("""
        UPDATE payroll 
        SET base_salary=%s, bonus=%s, deductions=%s, net_salary=%s 
        WHERE id=%s
    """, (base_salary, bonus, deductions, net_salary, payroll_id))

    db.commit()
    cursor.close()
    db.close()

    flash("Employee and salary details updated successfully.")
    return redirect(url_for("edit_employee_list"))

app.register_blueprint(employee_bp)

def sanitize_filename(email):
    return email.replace("@", "_at_").replace(".", "_")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login_form'))

if __name__=="__main__":
    app.run(debug=True)