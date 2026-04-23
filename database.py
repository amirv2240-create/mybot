import sqlite3

DB_NAME = "bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # جدول کاربران
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            role TEXT
        )
    """)

    # جدول شرکت‌ها
    c.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            company_name TEXT
        )
    """)

    # جدول دسته‌ها
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            company_username TEXT
        )
    """)

    # جدول فایل‌ها
    c.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            file_name TEXT,
            file_id TEXT,
            caption TEXT
        )
    """)

    conn.commit()
    conn.close()


def seed_users():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # کاربران تست
    try:
        c.execute("INSERT INTO users (username, role) VALUES (?, ?)", ("company1", "company"))
        c.execute("INSERT INTO users (username, role) VALUES (?, ?)", ("admin1", "admin"))
        c.execute("INSERT INTO users (username, role) VALUES (?, ?)", ("manager1", "manager"))
    except:
        pass

    # شرکت تست
    try:
        c.execute("INSERT INTO companies (username, company_name) VALUES (?, ?)", ("company1", "شرکت تست"))
    except:
        pass

    # دسته‌های تست
    try:
        c.execute("INSERT INTO categories (name, company_username) VALUES (?, ?)", ("دسته اول", "company1"))
        c.execute("INSERT INTO categories (name, company_username) VALUES (?, ?)", ("دسته دوم", "company1"))
    except:
        pass

    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, role FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result


def get_categories_by_company(company_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories WHERE company_username = ?", (company_username,))
    result = c.fetchall()
    conn.close()
    return result


def save_file_record(category_id, file_name, file_id, caption):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO files (category_id, file_name, file_id, caption)
        VALUES (?, ?, ?, ?)
    """, (category_id, file_name, file_id, caption))
    conn.commit()
    conn.close()


def add_company(username, company_name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO companies (username, company_name) VALUES (?, ?)", (username, company_name))
    conn.commit()
    conn.close()


def add_category(name, company_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, company_username) VALUES (?, ?)", (name, company_username))
    conn.commit()
    conn.close()


def get_all_companies():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT username, company_name FROM companies")
    result = c.fetchall()
    conn.close()
    return result


def get_categories_by_company_id(company_username):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, name FROM categories WHERE company_username = ?", (company_username,))
    result = c.fetchall()
    conn.close()
    return result


def get_all_files():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT files.id, files.file_name, files.file_id, categories.name
        FROM files
        JOIN categories ON files.category_id = categories.id
    """)
    result = c.fetchall()
    conn.close()
    return result


def add_user(username, role):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, role) VALUES (?, ?)", (username, role))
    conn.commit()
    conn.close()