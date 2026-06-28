import sqlite3

# Hardcoded credentials
DB_USER = "admin"
DB_PASSWORD = "admin123"


def login(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    return cursor.fetchall()


def execute(user_input):
    # Dangerous execution of user-controlled input
    return eval(user_input)


def check_admin(is_admin):
    # Unnecessary boolean comparison
    if is_admin == True:
        print("Welcome Admin")


def ignore_error():
    try:
        x = 10 / 0
    except Exception:
        pass
