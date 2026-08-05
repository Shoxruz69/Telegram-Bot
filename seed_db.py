import sqlite3

conn = sqlite3.connect('database/restaurant.db')
cursor = conn.cursor()

cursor.execute('DELETE FROM menu')
cursor.execute('DELETE FROM categories')
cursor.execute('DELETE FROM promotions')

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
    (4, 2, 'Issiq Kofe', "Xushbo'y kapuchino, ertalabki tetiklik uchun.", 15000, 'coffee.png'),
    (5, 3, 'Muzqaymoq', 'Vanil va qulupnayli shirin muzqaymoq.', 12000, 'ice_cream.png')
]
cursor.executemany('INSERT INTO menu (id, category_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?, ?)', menu_items)

promotions = [
    (1, 'Yozgi Super Aksiya', 'Fast Food taomlariga 15% chegirma!', 15, '2026-08-31 23:59', 1, None, 1),
    (2, 'Salqin Ichimliklar Aksiyasi', 'Barcha salqin ichimliklarga 20% chegirma!', 20, '2026-08-31 23:59', 2, None, 1)
]
cursor.executemany('''
    INSERT INTO promotions (id, title, description, discount_percent, end_date, category_id, menu_item_id, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', promotions)

conn.commit()
conn.close()
print("Database successfully seeded with categories, menu, and active promotions!")
