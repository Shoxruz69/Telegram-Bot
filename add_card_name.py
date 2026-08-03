import sqlite3

conn = sqlite3.connect('database/restaurant.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE settings ADD COLUMN card_name VARCHAR(100)')
    cursor.execute("UPDATE settings SET card_name = 'Ism Familiya'")
    conn.commit()
    print("Added card_name column.")
except Exception as e:
    print("Error:", e)

conn.close()
