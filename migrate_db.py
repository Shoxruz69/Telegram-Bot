import sqlite3

conn = sqlite3.connect('database/restaurant.db')
cursor = conn.cursor()

# Create Settings table
cursor.execute('''
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_number VARCHAR(100)
)
''')

# Create Orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    status VARCHAR(50),
    payment_method VARCHAR(50),
    receipt_image VARCHAR(500),
    total_amount INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
)
''')

# Insert default card number if empty
cursor.execute('SELECT COUNT(*) FROM settings')
if cursor.fetchone()[0] == 0:
    cursor.execute("INSERT INTO settings (card_number) VALUES ('8600 0000 0000 0000')")

conn.commit()
conn.close()
print("Migration completed successfully.")
