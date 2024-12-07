# employee task management system

#imports 
import os
import sys
import time
import datetime
import sqlite3
import random
import string
import hashlib
import getpass
import re 
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from cryptography.fernet import Fernet
#global variables
db_name = 'employee.db'
conn = sqlite3.connect(db_name)
c = conn.cursor()


# Generate a key for encryption and decryption
# You must keep this key safe. Anyone with this key can decrypt your data.
key = Fernet.generate_key()
cipher_suite = Fernet(key)



# Create the employees table
c.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    deadline TEXT,
    status TEXT NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees (id) 
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    employee_id INTEGER NOT NULL,
    FOREIGN KEY (task_id) REFERENCES tasks (id),
    FOREIGN KEY (employee_id) REFERENCES employees (id)
)
''')



# Commit the changes and close the connection
conn.commit()


# Create the assignments table

#functions

#function to create a new employee

def create_employee():
    print("Enter the following details to create a new employee")
    name = input("Enter the name of the employee: ")
    email = input("Enter the email of the employee: ")
    password = getpass.getpass("Enter the password of the employee: ") # getpass what does it do # 
    password = hashlib.md5(password.encode()).hexdigest()
    role = input("Enter the role of the employee: ")
    status = input("Enter the status of the employee: ")
    c.execute("INSERT INTO employees (name, email, password, role, status) VALUES (?, ?, ?, ?, ?)", (name, email, password, role, status))
    conn.commit()
    print("Employee created successfully")

#function to view all employees

def view_employees():
    c.execute("SELECT * FROM employees")
    employees = c.fetchall()
    for employee in employees:
        print(employee)

#function to update an employee

def update_employee():
    view_employees()
    id = input("Enter the id of the employee you want to update: ")
    print("Enter the following details to update the employee")
    name = input("Enter the name of the employee: ")
    email = input("Enter the email of the employee: ")
    password = getpass.getpass("Enter the password of the employee: ")
    password = hashlib.md5(password.encode()).hexdigest()
    role = input("Enter the role of the employee: ")
    status = input("Enter the status of the employee: ")
    c.execute("UPDATE employees SET name = ?, email = ?, password = ?, role = ?, status = ? WHERE id = ?", (name, email, password, role, status, id))
    conn.commit()
    print("Employee updated successfully")

#function to delete an employee

def delete_employee():
    view_employees()
    id = input("Enter the id of the employee you want to delete: ")
    c.execute("DELETE FROM employees WHERE id = ?", (id,))
    conn.commit()
    print("Employee deleted successfully")

#function to create a new task

def create_task():
    print("Enter the following details to create a new task")
    title = input("Enter the title of the task: ")
    description = input("Enter the description of the task: ")
    deadline = input("Enter the deadline of the task (YYYY-MM-DD): ")
    status = input("Enter the status of the task: ")
    employee_id = input("Enter the employee ID for this task: ")
    c.execute("INSERT INTO tasks (title, description, deadline, status, employee_id) VALUES (?, ?, ?, ?, ?)", (title, description, deadline, status, employee_id))
    conn.commit()
    print("Task created successfully")
#function to view all tasks

def view_tasks():
    c.execute("SELECT * FROM tasks")
    tasks = c.fetchall()
    for task in tasks:
        print(task)

#function to update a task

def update_task():
    view_tasks()
    id = input("Enter the id of the task you want to update: ")
    print("Enter the following details to update the task")
    title = input("Enter the title of the task: ")
    description = input("Enter the description of the task: ")
    deadline = input("Enter the deadline of the task (YYYY-MM-DD): ")
    status = input("Enter the status of the task: ")
    c.execute("UPDATE tasks SET title = ?, description = ?, deadline = ?, status = ? WHERE id = ?", (title, description, deadline, status, id))
    conn.commit()
    print("Task updated successfully")

#function to delete a task

def delete_task():
    view_tasks()
    id = input("Enter the id of the task you want to delete: ")
    c.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    print("Task deleted successfully")

#function to assign a task to an employee

def assign_task():
    view_tasks()
    task_id = input("Enter the id of the task you want to assign: ")
    view_employees()
    employee_id = input("Enter the id of the employee you want to assign the task to: ")
    c.execute("INSERT INTO assignments (task_id, employee_id) VALUES (?, ?)", (task_id, employee_id))
    conn.commit()
    print("Task assigned successfully")


#function to view all tasks assigned to an employee

def view_assigned_tasks():
    view_employees()
    employee_id = input("Enter the id of the employee to view assigned tasks: ")
    c.execute("SELECT * FROM assignments WHERE employee_id = ?", (employee_id,))
    assignments = c.fetchall()
    for assignment in assignments:
        task_id = assignment[1]
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        print(task)



#function to send email
def encode_password(password):
    encoded_password = cipher_suite.encrypt(password.encode())
    return encoded_password

def decode_password(encoded_password):
    decoded_password = cipher_suite.decrypt(encoded_password).decode() #
    return decoded_password


def send_email():
    from_email = input("Enter your email: ")
    password = getpass.getpass("Enter your password: ")
    encoded_password = encode_password(password)

    # Decode the password for demonstration purposes (not recommended in practice)
    decoded_password = decode_password(encoded_password)

    to_email = input("Enter the email of the recipient: ")
    subject = input("Enter the subject of the email: ")
    body = input("Enter the body of the email: ")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    
    text = msg.as_string()
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587) 
        server.starttls() 
        server.login(from_email, decoded_password)
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Please check your email and password.") 
    except Exception as e:
        print(f"An error occurred: {e}")



#function to validate email

def validate_email(email):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False
    

#function to validate password

def validate_password(password):
    if len(password) < 8:
        return False
    else:
        return True
    

#function to validate date

def validate_date(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    

#function to validate status

def validate_status(status):
    if status == "pending" or status == "in progress" or status == "completed":
        return True
    else:
        return False
    

#function to validate role

def validate_role(role):
    if role == "admin" or role == "employee":
        return True
    else:
        return False
    

#function to validate id

def validate_id(id):
    if id.isdigit():
        return True
    else:
        return False
    

#function to validate choice

def validate_choice(choice):
    if choice.isdigit():
        return True
    else:
        return False
    

#function to validate email exists

def validate_email_exists(email):

    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate email does not exist

def validate_email_does_not_exist(email):
    
        c.execute("SELECT * FROM employees WHERE email = ?", (email,))
        employee = c.fetchone()
        if employee:
            return False
        else:
            return True
        

#function to validate task exists

def validate_task_exists(id):
    c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = c.fetchone()
    if task:
        return True
    else:
        return False
    

#function to validate employee exists

def validate_employee_exists(id):
    c.execute("SELECT * FROM employees WHERE id = ?", (id,))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate assignment exists

def validate_assignment_exists(task_id, employee_id):
    c.execute("SELECT * FROM assignments WHERE task_id = ? AND employee_id = ?", (task_id, employee_id))
    assignment = c.fetchone()
    if assignment:
        return True
    else:
        return False
    

#function to validate assignment does not exist

def validate_assignment_does_not_exist(task_id, employee_id):

    c.execute("SELECT * FROM assignments WHERE task_id = ? AND employee_id = ?", (task_id, employee_id))
    assignment = c.fetchone()
    if assignment:
        return False
    else:
        return True
    

#function to validate email and password

def validate_email_and_password(email, password):
    password
    c.execute("SELECT * FROM employees WHERE email = ? AND password = ?", (email, password))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate email and role

def validate_email_and_role(email, role):
    c.execute("SELECT * FROM employees WHERE email = ? AND role = ?", (email, role))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate email and status

def validate_email_and_status(email, status):
    c.execute("SELECT * FROM employees WHERE email = ? AND status = ?", (email, status))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate email and id

def validate_email_and_id(email, id):
    c.execute("SELECT * FROM employees WHERE email = ? AND id = ?", (email, id))
    employee = c.fetchone()
    if employee:
        return True
    else:
        return False
    

#function to validate email and task id

def validate_email_and_task_id(email, id):
    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        c.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        task = c.fetchone()
        if task:
            return True
        else:
            return False
    else:
        return False
    

#function to validate email and employee id

def validate_email_and_employee_id(email, id):
    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        c.execute("SELECT * FROM employees WHERE id = ?", (id,))
        employee = c.fetchone()
        if employee:
            return True
        else:
            return False
    else:
        return False
    

#function to validate email and task id and employee id

def validate_email_and_task_id_and_employee_id(email, task_id, employee_id):
    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        if task:
            c.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            employee = c.fetchone()
            if employee:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
    

#function to validate email and task id and employee id and status

def validate_email_and_task_id_and_employee_id_and_status(email, task_id, employee_id, status):
    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        if task:
            c.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            employee = c.fetchone()
            if employee:
                if status == "pending" or status == "in progress" or status == "completed":
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False
    

#function to validate email and task id and employee id and status and id

def validate_email_and_task_id_and_employee_id_and_status_and_id(email, task_id, employee_id, status, id):
    c.execute("SELECT * FROM employees WHERE email = ?", (email,))
    employee = c.fetchone()
    if employee:
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = c.fetchone()
        if task:
            c.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            employee = c.fetchone()
            if employee:
                if status == "pending" or status == "in progress" or status == "completed":
                    c.execute("SELECT * FROM assignments WHERE task_id = ? AND employee_id = ?", (task_id, employee_id))
                    assignment = c.fetchone()
                    if assignment:
                        if id.isdigit():
                            return True
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False
    

    

# main function

def main():
    print("Welcome to the employee task management system")
    while True:
        print("1. Create Employee")
        print("2. View Employees")
        print("3. Update Employee")
        print("4. Delete Employee")
        print("5. Create Task")
        print("6. View Tasks")
        print("7. Update Task")
        print("8. Delete Task")
        print("9. Assign Task")
        print("10. View Assigned Tasks")
        print("11. Send Email")
        print("12. Exit")
        choice = input("Enter your choice: ")
        if choice == "1":
            create_employee()
        elif choice == "2":
            view_employees()
        elif choice == "3":
            update_employee()
        elif choice == "4":
            delete_employee()
        elif choice == "5":
            create_task()
        elif choice == "6":
            view_tasks()
        elif choice == "7":
            update_task()
        elif choice == "8":
            delete_task()
        elif choice == "9":
            assign_task()
        elif choice == "10":
            view_assigned_tasks()
        elif choice == "11":
            send_email()
        elif choice == "12":
            break
        else:
            print("Invalid choice. Please try again")
    conn.close()
    print("Thank you for using the employee task management system")


#calling the main function

if __name__ == "__main__":
    main()
