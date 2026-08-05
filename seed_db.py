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
    # ── Fast Food (Category 1) ──
    (1, 1, 'Gamburger', 'Katta va mazali ikki qavatli mol go\'shti gamburgeri, pishloq va yangi sabzavotlar bilan.', 35000, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=80'),
    (2, 1, 'Pepperoni Pitsa', 'Sifatli mozzarella pishlog\'i va italyancha pepperoni kolbasasidan tayyorlangan pitsa.', 80000, 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500&auto=format&fit=crop&q=80'),
    (3, 1, 'Cheeseburger', 'Sersuv mol go\'shti kotleti, erigan cheddar pishlog\'i va maxsus burger sousi.', 38000, 'https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=500&auto=format&fit=crop&q=80'),
    (4, 1, 'Tovuqli Lavash', 'Yumshoq tovuq go\'shti, qarsillama chips, bodring va sarimsoqli sous.', 32000, 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500&auto=format&fit=crop&q=80'),
    (5, 1, 'Klassik Hot-Dog', 'Qizdirilgan yumshoq bulochka, sersuv sosiska va xantal hamda ketchup bilan.', 22000, 'https://images.unsplash.com/photo-1619740455993-9e612b1af08a?w=500&auto=format&fit=crop&q=80'),
    (6, 1, 'Go\'shtli Donar', 'Yumshoq pishirilgan mol go\'shti bo\'laklari, sabzavotlar va ziravorlar.', 36000, 'https://images.unsplash.com/photo-1662116765994-1e22384a56a5?w=500&auto=format&fit=crop&q=80'),
    (7, 1, 'Tovuqli Naggets (8 ta)', 'Qarsillama oltinrang tovuq fileni bo\'laklari va pishloqli sous.', 28000, 'https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=80'),
    (8, 1, 'Klab Sendvich', 'Tost noni, kurka fileni, cheddar pishlog\'i, tuxum va kartoshka fri.', 42000, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500&auto=format&fit=crop&q=80'),
    (9, 1, 'Kartoshka Fri (Katta)', 'Qarsillama va issiq oltinrang kartoshka fri va tomat ketchup.', 18000, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=80'),
    (10, 1, 'Barbekyu Burger', 'Dudlangan barbekyu sousi, qarsillama piyoz halqalari va mol go\'shti kotleti.', 45000, 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500&auto=format&fit=crop&q=80'),

    # ── Ichimliklar (Category 2) ──
    (11, 2, 'Coca-Cola (0.5L)', 'Muzdek tetiklashtiruvchi salqin kola ichimligi.', 10000, 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=80'),
    (12, 2, 'Fanta Apelsin (0.5L)', 'Yorqin va shinavanda apelsinli gazlangan ichimlik.', 10000, 'https://images.unsplash.com/photo-1624517452488-04869289c4ca?w=500&auto=format&fit=crop&q=80'),
    (13, 2, 'Sprite (0.5L)', 'Laym va limon ta\'mli salqinlashtiruvchi ichimlik.', 10000, 'https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=500&auto=format&fit=crop&q=80'),
    (14, 2, 'Klassik Moxito (0.5L)', 'Yalpiz, laym va muzli tabiiy salqin mexnat ichimligi.', 22000, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80'),
    (15, 2, 'Kapuchino Kofe', 'Xushbo\'y arabika espresso va yumshoq sut ko\'pigi.', 18000, 'https://images.unsplash.com/photo-1534778101976-62847782c213?w=500&auto=format&fit=crop&q=80'),
    (16, 2, 'Latte Kofe', 'Mayin va silliq sutli espresso kofesi.', 20000, 'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=500&auto=format&fit=crop&q=80'),
    (17, 2, 'Apelsin Sharbati', '100% tabiiy va yangi siqilgan apelsin sharbati.', 25000, 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=500&auto=format&fit=crop&q=80'),
    (18, 2, 'Muzli Choy (Limonli)', 'Yalpiz va limon bo\'laklari bilan tayyorlangan salqin muzli choy.', 15000, 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&auto=format&fit=crop&q=80'),
    (19, 2, 'Qora Choy (Choynak)', 'Oliy navli tog\' qora choyi.', 8000, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format&fit=crop&q=80'),
    (20, 2, 'Ko\'k Choy (Choynak)', 'Yalpizli tetiklashtiruvchi ko\'k choy.', 8000, 'https://images.unsplash.com/photo-1627435601361-ec25f5b1d0e5?w=500&auto=format&fit=crop&q=80'),

    # ── Shirinliklar (Category 3) ──
    (21, 3, 'Vanilli Muzqaymoq', 'Qulupnay va shokolad toppingli qaymoqli vanil muzqaymog\'i.', 15000, 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=500&auto=format&fit=crop&q=80'),
    (22, 3, 'Nyu-York Chizkeyk', 'Mayin pishloqli va rezavor meva sousli klassik desert.', 32000, 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&auto=format&fit=crop&q=80'),
    (23, 3, 'Tiramisu Deserti', 'Italiyacha kofe va maskarpone pishloqli mayin desert.', 35000, 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop&q=80'),
    (24, 3, 'Shokoladli Fondan', 'Ichidan issiq erigan shokolad oqib chiquvchi pishiriq va vanil muzqaymoq.', 28000, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=80'),
    (25, 3, 'Shokoladli Donut', 'Shokoladli glazur va rangli sepmalar bilan bezatilgan ponchik.', 14000, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80'),
    (26, 3, 'San-Sebastian Chizkeyk', 'Ust qismi oltinrang kuygan uslubdagi mayin ispan pishloqli torti.', 38000, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=80'),
    (27, 3, 'Belgiya Vaflisi', 'Banan, nutella va vanil muzqaymoq sharigi bilan belgiya vaflisi.', 30000, 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?w=500&auto=format&fit=crop&q=80'),
    (28, 3, 'Asalli Medovik', 'Tabiiy asal va qaymoqli kremdan ko\'p qavatli yumshoq tort.', 26000, 'https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=500&auto=format&fit=crop&q=80'),
    (29, 3, 'Turk Pahlavasi', 'Yong\'oqli va asal qiyomli sharqona ko\'p qavatli pahlava.', 25000, 'https://images.unsplash.com/photo-1519676867240-f03562e64548?w=500&auto=format&fit=crop&q=80'),
    (30, 3, 'Mevali Tart', 'Yangi rezavor mevalar va vanilli krem bilan tayyorlangan pishiriq.', 27000, 'https://images.unsplash.com/photo-1519869325930-281384150729?w=500&auto=format&fit=crop&q=80')
]

cursor.executemany('INSERT INTO menu (id, category_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?, ?)', menu_items)

conn.commit()
conn.close()
print("30 ta taom (har bir kategoriyaga 10 tadan) rasm va tavsiflari bilan muvaffaqiyatli bazaga qo'shildi!")
