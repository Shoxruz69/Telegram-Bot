import sqlite3

conn = sqlite3.connect('database/restaurant.db')
cursor = conn.cursor()

# Clear existing menu
cursor.execute('DELETE FROM menu')
# Ensure categories are there
cursor.execute('DELETE FROM categories')

categories = [
    (1, 'Fast Food'),
    (2, 'Ichimliklar'),
    (3, 'Shirinliklar')
]
cursor.executemany('INSERT INTO categories (id, name) VALUES (?, ?)', categories)

menu_items = [
    (1, 1, 'Gamburger', 'Katta va mazali ikki qavatli gamburger, pishloq bilan.', 35000, 'hamburger.png'),
    (2, 1, 'Pitsa', 'Sifatli pishloq va pepperoni kolbasasidan tayyorlangan pitsa.', 80000, 'pizza.png'),
    (3, 2, 'Kola (Muzdek)', 'Yozning issiq kunlarida muzdek kola.', 10000, 'cola.png'),
    (4, 2, 'Issiq Kofe', 'Xushbo\'y kapuchino, ertalabki tetiklik uchun.', 15000, 'coffee.png'),
    (5, 3, 'Muzqaymoq', 'Vanil va qulupnayli shirin muzqaymoq.', 12000, 'ice_cream.png')
]
cursor.executemany('INSERT INTO menu (id, category_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?, ?)', menu_items)

conn.commit()
conn.close()
print("Database seeded with images!")
