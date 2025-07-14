# ⚙️ EMS Project Setup Guide

This document provides setup instructions for creating the required `.env` file and configuring the MySQL database structure for the Employee Management System.

---

## 📄 Setup for `.env` File

Create a file named `.env` in the root directory of the project and add the following content:

```ini
SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=ems
```
---
## 🗄️ MySQL Database Schema

Run the following SQL commands in your MySQL console to set up the EMS database and required tables:

```sql
-- Create the database
CREATE DATABASE ems;
USE ems;

-- Employee Table
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(20),
    password VARCHAR(255),
    photo_path VARCHAR(255)
);

-- Attendance Table
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    date DATE,
    status VARCHAR(10),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Leave Requests Table
CREATE TABLE leave_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    from_date DATE,
    to_date DATE,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

-- Payroll Table
CREATE TABLE payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    month VARCHAR(20),
    year INT,
    base_salary DECIMAL(10,2),
    bonus DECIMAL(10,2),
    deductions DECIMAL(10,2),
    net_salary DECIMAL(10,2),
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
