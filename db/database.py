
import sqlite3
from data.menu_data import menu
from data.hours_data import opening_hours

DB = "db/restaurant.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS opening_hours (days TEXT, Open TEXT, close TEXT, note TEXT)')
        cursor.execute('CREATE TABLE IF NOT EXISTS menu (category TEXT, item_name TEXT, description TEXT, price REAL)')
        cursor.execute('''CREATE TABLE IF NOT EXISTS reservation (
            reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT, last_name TEXT,
            year INTEGER, month INTEGER, day INTEGER,
            time TEXT, status TEXT
        )''')
        if cursor.execute("SELECT COUNT(*) FROM opening_hours").fetchone()[0] == 0:
            for day, info in opening_hours.items():
                cursor.execute("INSERT INTO opening_hours (days, Open, close, note) VALUES (?,?,?,?)",
                               (day, info["opens"], info["closes"], info["note"]))
        if cursor.execute("SELECT COUNT(*) FROM menu").fetchone()[0] == 0:
            for category, items in menu.items():
                for item in items:
                    cursor.execute("INSERT INTO menu (category, item_name, description, price) VALUES (?,?,?,?)",
                                   (category, item["item_name"], item["description"], item["price"]))
        conn.commit()

def get_details_category_all(category):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM menu WHERE category = ?', (category.lower(),))
        results = cursor.fetchall()
        return [{"item_name": row[1], "description": row[2], "price": row[3]} for row in results]

def get_details_opening_time_all():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM opening_hours')
        results = cursor.fetchall()
        return [{"day": row[0], "opens": row[1], "closes": row[2], "note": row[3]} for row in results]

def create_reservation(first_name, last_name, year, month, day, time):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO reservation (first_name, last_name, year, month, day, time, status) VALUES (?,?,?,?,?,?,?)',
            (first_name.lower(), last_name.lower(), year, month, day, time, "confirmed")
        )
        conn.commit()
        return cursor.lastrowid

def check_reservation_db(first_name, last_name):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM reservation WHERE first_name = ? AND last_name = ?',
                       (first_name.lower(), last_name.lower()))
        results = cursor.fetchall()
        if not results:
            return []
        return [{"reservation_id": r[0], "first_name": r[1], "last_name": r[2],
                 "year": r[3], "month": r[4], "day": r[5], "time": r[6], "status": r[7]} for r in results]

def cancel_reservation_db(first_name, last_name):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE reservation SET status = ? WHERE first_name = ? AND last_name = ?',
                       ("cancelled", first_name.lower(), last_name.lower()))
        conn.commit()
        if cursor.rowcount == 0:
            return None
        cursor.execute('SELECT * FROM reservation WHERE first_name = ? AND last_name = ?',
                       (first_name.lower(), last_name.lower()))
        row = cursor.fetchone()
        return {"reservation_id": row[0], "first_name": row[1], "last_name": row[2],
                "year": row[3], "month": row[4], "day": row[5], "time": row[6], "status": row[7]}
