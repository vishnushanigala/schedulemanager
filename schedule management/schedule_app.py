import streamlit as st
import sqlite3
from datetime import datetime

# Initialize SQLite database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_date TEXT NOT NULL
)
''')
conn.commit()

# Function to register a new user
def register_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
        conn.commit()
        st.success("Registration successful!")
        st.experimental_rerun()  # Reload the page after registration
    except sqlite3.IntegrityError:
        st.error("Username already exists!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Function to login
def login(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        st.session_state.username = username  # Store username in session state
        return True
    else:
        return False

# Function to logout
def logout():
    st.session_state.login_state = False
    st.success("Logged out successfully!")
    st.experimental_rerun()  # Reload the page after logout

# Function to add a new task
def add_task(task_name, task_description, task_date):
    try:
        cursor.execute("INSERT INTO tasks (task_name, task_description, task_date) VALUES (?, ?, ?)",
                       (task_name, task_description, task_date))
        conn.commit()
        st.success(f"Task '{task_name}' added successfully with description '{task_description}' on '{task_date}'!")
    except Exception as e:
        st.error(f"An error occurred while adding the task: {e}")

# Function to delete a task
def delete_task(task_id):
    try:
        # Get the task details before deleting
        task_to_delete = cursor.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        
        if task_to_delete:
            cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            st.success(f"Task '{task_to_delete[1]}' with description '{task_to_delete[2]}' deleted successfully!")
        else:
            st.error("Task not found!")
    except Exception as e:
        st.error(f"An error occurred while deleting the task: {e}")

# Function to display admin panel
def admin_panel():
    st.title("Admin Panel")
    
    st.subheader("User Data")
    users = cursor.execute("SELECT * FROM users").fetchall()
    if users:
        st.write("ID\tUsername\tPassword")
        for user in users:
            st.write(f"{user[0]}\t{user[1]}\t{user[2]}")  # Note: Passwords are hashed
    else:
        st.info("No user data available.")
    
    st.subheader("Task Data")
    tasks = cursor.execute("SELECT * FROM tasks").fetchall()
    if tasks:
        st.write("ID\tTask Name\tTask Description\tTask Date")
        for task in tasks:
            st.write(f"{task[0]}\t{task[1]}\t{task[2]}\t{task[3]}")
    else:
        st.info("No task data available.")

# Streamlit UI
def main():
    st.title("Schedule Management App")
    
    # Initialize session state
    if 'login_state' not in st.session_state:
        st.session_state.login_state = False
    
    menu = st.sidebar.selectbox("Menu", ["Login", "Register", "Admin Panel"])
    
    if menu == "Login" and not st.session_state.login_state:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if login(username, password):
                st.session_state.login_state = True
                st.success("Logged in successfully!")
                task_menu(st.session_state.username)
            else:
                st.error("Invalid username or password!")
    
    elif menu == "Register":
        st.subheader("Register")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if new_password == confirm_password:
            if st.button("Register"):
                register_user(new_username, new_password)
        else:
            st.error("Passwords do not match!")
            
    elif st.session_state.login_state:
        if menu == "Admin Panel":
            admin_panel()
        else:
            task_menu(st.session_state.username)

# Task management UI
def task_menu(username):
    st.subheader(f"Hello, {username}!")
    st.subheader("Task Management")
    
    task_name = st.text_input("Task Name")
    task_description = st.text_area("Task Description")
    task_date = st.date_input("Task Date", value=datetime.today())
    
    if st.button("Add Task"):
        add_task(task_name, task_description, task_date)
    
    tasks = cursor.execute("SELECT * FROM tasks").fetchall()
    
    if tasks:
        st.subheader("Current Tasks")
        for task in tasks:
            st.write(f"ID: {task[0]}, Name: {task[1]}, Date: {task[3]}")
        
        task_to_delete = st.selectbox("Select task to delete", [task[1] for task in tasks])
        if st.button("Delete Task"):
            delete_task(tasks[[task[1] for task in tasks].index(task_to_delete)][0])
    
    else:
        st.info("No tasks available.")
    
    if st.button("Logout"):
        logout()

if __name__ == "__main__":
    main()
