from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import connect_db
from datetime import date
import cv2, os
from deepface import DeepFace

employee_bp=Blueprint('employee',__name__)
@employee_bp.route('/employee_dashboard')
def employee_dashboard():
    if session.get('role')!='employee':
        return "Access Denied", 403
    name=session.get('username')
    return render_template('employee_dashboard.html',name=name)

@employee_bp.route("/change_password", methods=["GET", "POST"])
def change_password():
    if session.get("role") != "employee":
        return "Access Denied", 403

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("New passwords do not match!", "error")
            return redirect(url_for("employee.change_password"))

        db = connect_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT password FROM employees WHERE id = %s", (session["id"],))
        user = cursor.fetchone()

        if not user or not check_password_hash(user["password"], current_password):
            flash("Current password is incorrect!", "error")
            return redirect(url_for("employee.change_password"))

        new_hashed = generate_password_hash(new_password)
        cursor.execute("UPDATE employees SET password = %s WHERE id = %s", (new_hashed, session["id"]))
        db.commit()
        cursor.close()
        db.close()


        return redirect(url_for("employee.employee_dashboard"))

    return render_template("change_password.html")

@employee_bp.route("/my_attendance")
def my_attendance():
    if session.get("role") != "employee":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT date, status 
        FROM attendance 
        WHERE employee_id = %s 
        ORDER BY date DESC
    """, (session["id"],))

    attendance_records = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("my_attendance.html", records=attendance_records, name=session.get("username"))


@employee_bp.route("/apply_leave", methods=["GET", "POST"])
def apply_leave():
    if session.get("role") != "employee":
        return "Access Denied", 403

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        from_date = request.form["from_date"]
        to_date = request.form["to_date"]
        reason = request.form["reason"]

        cursor.execute("""
            INSERT INTO leave_requests (employee_id, from_date, to_date, reason, status)
            VALUES (%s, %s, %s, %s, 'Pending')
        """, (session["id"], from_date, to_date, reason))
        db.commit()

        return redirect(url_for("employee.employee_dashboard", success="2"))

    # Fetch leave history
    cursor.execute("""
        SELECT from_date, to_date, reason, status 
        FROM leave_requests 
        WHERE employee_id = %s 
        ORDER BY from_date DESC
    """, (session["id"],))
    leave_history = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("apply_leave.html", name=session.get("username"), leave_history=leave_history)
 # or adjust this import if needed

@employee_bp.route("/face_attendance", methods=["GET"])
def face_attendance():
    if session.get("role") != "employee":
        return "Access Denied", 403

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Camera failed"

    temp_path = "temp.jpg"
    cv2.imwrite(temp_path, frame)

    db = connect_db()
    cursor = db.cursor(dictionary=True)

    user_id = session.get("id")
    user_email = session.get("email")

    matched = False
    face_path = os.path.join("static/faces", f"{user_email}.jpg")

    try:
        result = DeepFace.verify(
            temp_path,
            face_path,
            model_name="ArcFace",
            detector_backend="retinaface",
            distance_metric="cosine",
            enforce_detection=False
        )

        distance = result["distance"]
        threshold = 0.6  # tweak this if needed

        if distance <= threshold:
            today = date.today()
            cursor.execute("SELECT * FROM attendance WHERE employee_id=%s AND date=%s", (user_id, today))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO attendance (employee_id, date, status) VALUES (%s, %s, %s)",
                               (user_id, today, 'Present'))
                db.commit()
            matched = True

    except Exception as e:
        print("Verification failed:", e)

    cursor.close()
    db.close()

    os.remove(temp_path)  # clean up temp image

    if matched:
        return render_template("face_attendance_result.html", result="✅ Attendance marked!")
    else:
        return render_template("face_attendance_result.html", result="❌ Face not recognized. Try again.")

