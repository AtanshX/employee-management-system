# 🧑‍💼 Employee Management System (EMS) - Flask Web App

This is a **full-featured Employee Management System** built using **Flask**, **MySQL**, and **HTML/CSS**. It supports **admin and employee roles**, with modules for:

- 👥 Employee CRUD (Create, Read, Update, Delete)
- 📅 Leave Management
- 📊 Attendance Tracking (including face recognition)
- 💰 Payroll Management
- 🔒 Authentication and Password Management

---

## 🚀 Features

### Admin Panel
- Add, edit, delete employees
- Set base salary and manage payroll
- View and handle leave requests
- View complete attendance records

### Employee Panel
- Apply for leave
- View personal attendance
- Mark attendance via facial recognition (DeepFace)
- Change password

---

## 💻 Tech Stack

- **Backend**: Python, Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS (Glassmorphism Style)
- **Face Recognition**: DeepFace
- **Security**: Password hashing using `werkzeug.security`
- **Environment Handling**: `.env` for sensitive data (recommended)

---

## 📷 Face Recognition

Employees can mark attendance using webcam-based face recognition.
- Photos stored in `static/faces/`
- Matching handled via DeepFace

---

## 🧠 Developed By

**Atansh Dhiman**  
Computer Engineering Student, Thapar University

---

