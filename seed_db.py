import sqlite3

conn = sqlite3.connect('database/restaurant.db')
cursor = conn.cursor()

# Check and add columns if not present
def ensure_column(table, col_name, col_type):
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    if col_name not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")

ensure_column('categories', 'name_ru', 'TEXT')
ensure_column('categories', 'name_en', 'TEXT')

ensure_column('menu', 'name_ru', 'TEXT')
ensure_column('menu', 'name_en', 'TEXT')
ensure_column('menu', 'description_ru', 'TEXT')
ensure_column('menu', 'description_en', 'TEXT')
ensure_column('menu', 'old_price', 'INTEGER DEFAULT 0')

ensure_column('promotions', 'title_ru', 'TEXT')
ensure_column('promotions', 'title_en', 'TEXT')
ensure_column('promotions', 'description_ru', 'TEXT')
ensure_column('promotions', 'description_en', 'TEXT')

# Clear old data
cursor.execute('DELETE FROM menu')
cursor.execute('DELETE FROM categories')
cursor.execute('DELETE FROM promotions')

# ── CATEGORIES (UZ, RU, EN) ──
categories = [
    (1, 'Fast Food', 'Фастфуд', 'Fast Food'),
    (2, 'Ichimliklar', 'Напитки', 'Drinks'),
    (3, 'Shirinliklar', 'Десерты', 'Desserts'),
    (4, 'Combo Set', 'Комбо наборы', 'Combo Sets')
]
cursor.executemany('INSERT INTO categories (id, name, name_ru, name_en) VALUES (?, ?, ?, ?)', categories)

# ── MENU ITEMS (35 items with UZ, RU, EN) ──
menu_items = [
    # ── Fast Food (Category 1) ──
    (1, 1, 'Gamburger', 'Гамбургер', 'Hamburger', 
     'Katta va mazali ikki qavatli mol go\'shti gamburgeri, pishloq va yangi sabzavotlar bilan.', 
     'Большой сочный бургер с двойной говяжьей котлетой, сыром и свежими овощами.', 
     'Big and juicy double beef burger with melted cheese and fresh vegetables.', 
     35000, 0, 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=80'),

    (2, 1, 'Pepperoni Pitsa', 'Пепперони пицца', 'Pepperoni Pizza', 
     'Sifatli mozzarella pishlog\'i va italyancha pepperoni kolbasasidan tayyorlangan pitsa.', 
     'Пицца с сыром моцарелла и настоящими итальянскими колбасками пепперони.', 
     'Pizza with premium mozzarella cheese and authentic Italian pepperoni.', 
     80000, 0, 'https://images.unsplash.com/photo-1628840042765-356cda07504e?w=500&auto=format&fit=crop&q=80'),

    (3, 1, 'Cheeseburger', 'Чизбургер', 'Cheeseburger', 
     'Sersuv mol go\'shti kotleti, erigan cheddar pishlog\'i va maxsus burger sousi.', 
     'Сочная говяжья котлета, расплавленный сыр чеддер и фирменный соус.', 
     'Juicy beef patty, melted cheddar cheese, and signature burger sauce.', 
     38000, 0, 'https://images.unsplash.com/photo-1572802419224-296b0aeee0d9?w=500&auto=format&fit=crop&q=80'),

    (4, 1, 'Tovuqli Lavash', 'Куриный лаваш', 'Chicken Lavash', 
     'Yumshoq tovuq go\'shti, qarsillama chips, bodring va sarimsoqli sous.', 
     'Нежное куриное филе, хрустящие чипсы, свежие огурцы и чесночный соус.', 
     'Tender chicken fillet, crunchy chips, fresh cucumbers, and garlic sauce.', 
     32000, 0, 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500&auto=format&fit=crop&q=80'),

    (5, 1, 'Klassik Hot-Dog', 'Классический хот-дог', 'Classic Hot Dog', 
     'Qizdirilgan yumshoq bulochka, sersuv sosiska va xantal hamda ketchup bilan.', 
     'Теплая булочка, сочная сосиска с горчицей и томатным кетчупом.', 
     'Warm bun, juicy sausage topped with mustard and tomato ketchup.', 
     22000, 0, 'https://images.unsplash.com/photo-1619740455993-9e612b1af08a?w=500&auto=format&fit=crop&q=80'),

    (6, 1, 'Go\'shtli Donar', 'Мясной донар', 'Beef Doner', 
     'Yumshoq pishirilgan mol go\'shti bo\'laklari, sabzavotlar va ziravorlar.', 
     'Ароматные ломтики нежной говядины со свежими овощами и специями.', 
     'Tender slices of seasoned beef with fresh vegetables and special spices.', 
     36000, 0, 'https://images.unsplash.com/photo-1662116765994-1e22384a56a5?w=500&auto=format&fit=crop&q=80'),

    (7, 1, 'Tovuqli Naggets (8 ta)', 'Куриные наггетсы (8 шт)', 'Chicken Nuggets (8 pcs)', 
     'Qarsillama oltinrang tovuq fileni bo\'laklari va pishloqli sous.', 
     'Хрустящие золотистые кусочки куриного филе с сырным соусом.', 
     'Crispy golden chicken breast nuggets served with cheese sauce.', 
     28000, 0, 'https://images.unsplash.com/photo-1562967914-608f82629710?w=500&auto=format&fit=crop&q=80'),

    (8, 1, 'Klab Sendvich', 'Клаб сэндвич', 'Club Sandwich', 
     'Tost noni, kurka fileni, cheddar pishlog\'i, tuxum va kartoshka fri.', 
     'Поджаренный тост, филе индейки, сыр чеддер, яйцо и картофель фри.', 
     'Toasted bread, turkey fillet, cheddar cheese, egg, and french fries.', 
     42000, 0, 'https://images.unsplash.com/photo-1528735602780-2552fd46c7af?w=500&auto=format&fit=crop&q=80'),

    (9, 1, 'Kartoshka Fri (Katta)', 'Картофель фри (Большой)', 'French Fries (Large)', 
     'Qarsillama va issiq oltinrang kartoshka fri va tomat ketchup.', 
     'Горячий золотистый картофель фри с томатным кетчупом.', 
     'Hot and crispy golden french fries served with tomato ketchup.', 
     18000, 0, 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=500&auto=format&fit=crop&q=80'),

    (10, 1, 'Barbekyu Burger', 'Барбекю бургер', 'BBQ Burger', 
     'Dudlangan barbekyu sousi, qarsillama piyoz halqalari va mol go\'shti kotleti.', 
     'Дымный соус барбекю, хрустящие луковые кольца и говяжья котлета.', 
     'Smoky BBQ sauce, crispy onion rings, and juicy beef patty.', 
     45000, 0, 'https://images.unsplash.com/photo-1586190848861-99aa4a171e90?w=500&auto=format&fit=crop&q=80'),

    # ── Ichimliklar (Category 2) ──
    (11, 2, 'Coca-Cola (0.5L)', 'Coca-Cola (0.5л)', 'Coca-Cola (0.5L)', 
     'Muzdek tetiklashtiruvchi salqin kola ichimligi.', 
     'Ледяная освежающая газировка кока-кола.', 
     'Ice-cold refreshing cola beverage.', 
     10000, 0, 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=500&auto=format&fit=crop&q=80'),

    (12, 2, 'Fanta Apelsin (0.5L)', 'Fanta Апельсин (0.5л)', 'Fanta Orange (0.5L)', 
     'Yorqin va shinavanda apelsinli gazlangan ichimlik.', 
     'Яркий и сочный апельсиновый газированный напиток.', 
     'Bright and sparkling orange soda.', 
     10000, 0, 'https://images.unsplash.com/photo-1624517452488-04869289c4ca?w=500&auto=format&fit=crop&q=80'),

    (13, 2, 'Sprite (0.5L)', 'Sprite (0.5л)', 'Sprite (0.5L)', 
     'Laym va limon ta\'mli salqinlashtiruvchi ichimlik.', 
     'Освежающий напиток со вкусом лайма и лимона.', 
     'Crisp lemon-lime refreshing drink.', 
     10000, 0, 'https://images.unsplash.com/photo-1625772299848-391b6a87d7b3?w=500&auto=format&fit=crop&q=80'),

    (14, 2, 'Klassik Moxito (0.5L)', 'Классический мохито (0.5л)', 'Classic Mojito (0.5L)', 
     'Yalpiz, laym va muzli tabiiy salqin mexnat ichimligi.', 
     'Натуральный прохладительный напиток с мятой, лаймом и льдом.', 
     'Natural refreshing drink with fresh mint, lime, and ice.', 
     22000, 0, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80'),

    (15, 2, 'Kapuchino Kofe', 'Кофе Капучино', 'Cappuccino Coffee', 
     'Xushbo\'y arabika espresso va yumshoq sut ko\'pigi.', 
     'Ароматный эспрессо из арабики с нежной молочной пенкой.', 
     'Rich arabica espresso topped with creamy velvety milk foam.', 
     18000, 0, 'https://images.unsplash.com/photo-1534778101976-62847782c213?w=500&auto=format&fit=crop&q=80'),

    (16, 2, 'Latte Kofe', 'Кофе Латте', 'Latte Coffee', 
     'Mayin va silliq sutli espresso kofesi.', 
     'Мягкий и нежный кофе эспрессо с горячим молоком.', 
     'Smooth and delicate espresso with steamed milk.', 
     20000, 0, 'https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=500&auto=format&fit=crop&q=80'),

    (17, 2, 'Apelsin Sharbati', 'Апельсиновый сок', 'Orange Juice', 
     '100% tabiiy va yangi siqilgan apelsin sharbati.', 
     '100% натуральный свежевыжатый апельсиновый сок.', 
     '100% natural freshly squeezed orange juice.', 
     25000, 0, 'https://images.unsplash.com/photo-1613478223719-2ab802602423?w=500&auto=format&fit=crop&q=80'),

    (18, 2, 'Muzli Choy (Limonli)', 'Холодный чай (Лимонный)', 'Iced Tea (Lemon)', 
     'Yalpiz va limon bo\'laklari bilan tayyorlangan salqin muzli choy.', 
     'Освежающий холодный чай с мятой и дольками лимона.', 
     'Refreshing iced tea brewed with fresh mint and lemon slices.', 
     15000, 0, 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=500&auto=format&fit=crop&q=80'),

    (19, 2, 'Qora Choy (Choynak)', 'Черный чай (Чайник)', 'Black Tea (Pot)', 
     'Oliy navli tog\' qora choyi.', 
     'Высокогорный ароматный черный чай высшего сорта.', 
     'Premium mountain black tea.', 
     8000, 0, 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=500&auto=format&fit=crop&q=80'),

    (20, 2, 'Ko\'k Choy (Choynak)', 'Зеленый чай (Чайник)', 'Green Tea (Pot)', 
     'Yalpizli tetiklashtiruvchi ko\'k choy.', 
     'Освежающий зеленый чай с листьями мяты.', 
     'Refreshing green tea with mint.', 
     8000, 0, 'https://images.unsplash.com/photo-1627435601361-ec25f5b1d0e5?w=500&auto=format&fit=crop&q=80'),

    # ── Shirinliklar (Category 3) ──
    (21, 3, 'Vanilli Muzqaymoq', 'Ванильное мороженое', 'Vanilla Ice Cream', 
     'Qulupnay va shokolad toppingli qaymoqli vanil muzqaymog\'i.', 
     'Сливочное ванильное мороженое с клубничным и шоколадным топпингом.', 
     'Creamy vanilla ice cream topped with strawberry and chocolate syrup.', 
     15000, 0, 'https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=500&auto=format&fit=crop&q=80'),

    (22, 3, 'Nyu-York Chizkeyk', 'Чизкейк Нью-Йорк', 'New York Cheesecake', 
     'Mayin pishloqli va rezavor meva sousli klassik desert.', 
     'Классический сливочный чизкейк с ягодным соусом.', 
     'Classic creamy cheesecake served with berry sauce.', 
     32000, 0, 'https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=500&auto=format&fit=crop&q=80'),

    (23, 3, 'Tiramisu Deserti', 'Десерт Тирамису', 'Tiramisu Dessert', 
     'Italiyacha kofe va maskarpone pishloqli mayin desert.', 
     'Нежнейший итальянский десерт с кофе и сыром маскарпоне.', 
     'Authentic Italian dessert infused with espresso and mascarpone.', 
     35000, 0, 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=500&auto=format&fit=crop&q=80'),

    (24, 3, 'Shokoladli Fondan', 'Шоколадный фондан', 'Chocolate Fondant', 
     'Ichidan issiq erigan shokolad oqib chiquvchi pishiriq va vanil muzqaymoq.', 
     'Теплый десерт с жидким шоколадом внутри и шариком мороженого.', 
     'Warm cake with molten chocolate core served with vanilla ice cream.', 
     28000, 0, 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=500&auto=format&fit=crop&q=80'),

    (25, 3, 'Shokoladli Donut', 'Шоколадный пончик', 'Chocolate Donut', 
     'Shokoladli glazur va rangli sepmalar bilan bezatilgan ponchik.', 
     'Пышный пончик с шоколадной глазурью и цветной посыпкой.', 
     'Fluffy donut with chocolate glaze and colorful sprinkles.', 
     14000, 0, 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?w=500&auto=format&fit=crop&q=80'),

    (26, 3, 'San-Sebastian Chizkeyk', 'Чизкейк Сан-Себастьян', 'San Sebastian Cheesecake', 
     'Ust qismi oltinrang kuygan uslubdagi mayin ispan pishloqli torti.', 
     'Нежный баскский обожженный чизкейк с карамельной корочкой.', 
     'Creamy Basque burnt cheesecake with caramelized crust.', 
     38000, 0, 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=80'),

    (27, 3, 'Belgiya Vaflisi', 'Бельгийские вафли', 'Belgian Waffle', 
     'Banan, nutella va vanil muzqaymoq sharigi bilan belgiya vaflisi.', 
     'Хрустящая вафля с бананом, нутеллой и шариком мороженого.', 
     'Crispy waffle served with fresh banana, Nutella, and ice cream.', 
     30000, 0, 'https://images.unsplash.com/photo-1562376552-0d160a2f238d?w=500&auto=format&fit=crop&q=80'),

    (28, 3, 'Asalli Medovik', 'Медовик с медом', 'Honey Cake (Medovik)', 
     'Tabiiy asal va qaymoqli kremdan ko\'p qavatli yumshoq tort.', 
     'Многослойный нежный торт из натурального меда и сметанного крема.', 
     'Multi-layered soft cake crafted with natural honey and cream.', 
     26000, 0, 'https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?w=500&auto=format&fit=crop&q=80'),

    (29, 3, 'Turk Pahlavasi', 'Турецкая пахлава', 'Turkish Baklava', 
     'Yong\'oqli va asal qiyomli sharqona ko\'p qavatli pahlava.', 
     'Восточная многослойная пахлава с грецкими орехами и медовым сиропом.', 
     'Flaky oriental pastry layered with walnuts and honey syrup.', 
     25000, 0, 'https://images.unsplash.com/photo-1519676867240-f03562e64548?w=500&auto=format&fit=crop&q=80'),

    (30, 3, 'Mevali Tart', 'Фруктовый тарт', 'Fruit Tart', 
     'Yangi rezavor mevalar va vanilli krem bilan tayyorlangan pishiriq.', 
     'Хрустящая корзинка со свежими ягодами и ванильным кремом.', 
     'Crisp pastry filled with rich vanilla cream and fresh berries.', 
     27000, 0, 'https://images.unsplash.com/photo-1519869325930-281384150729?w=500&auto=format&fit=crop&q=80'),

    # ── Combo Set (Category 4) ──
    (31, 4, 'Combo Fast & Cold', 'Комбо Fast & Cold', 'Combo Fast & Cold', 
     'Gamburger + Kartoshka fri + Coca-Cola 0.5L + ketchup va pishloqli sous.', 
     'Гамбургер + Картофель фри + Coca-Cola 0.5л + кетчуп и сырный соус.', 
     'Hamburger + French Fries + Coca-Cola 0.5L + ketchup & cheese sauce.', 
     55000, 0, 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f6?w=500&auto=format&fit=crop&q=80'),

    (32, 4, 'Combo Pizza Family', 'Комбо Pizza Family', 'Combo Pizza Family', 
     'Pepperoni Pitsa (katta) + 2 ta Coca-Cola 0.5L + Tovuqli Naggets (8 ta).', 
     'Пепперони пицца (большая) + 2 шт Coca-Cola 0.5л + Наггетсы (8 шт).', 
     'Pepperoni Pizza (Large) + 2x Coca-Cola 0.5L + Chicken Nuggets (8 pcs).', 
     110000, 0, 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=80'),

    (33, 4, 'Combo Cheesy Burger', 'Комбо Cheesy Burger', 'Combo Cheesy Burger', 
     'Cheeseburger + Kartoshka fri (katta) + Klassik Moxito salqin ichimligi.', 
     'Чизбургер + Картофель фри (большой) + Освежающий Мохито.', 
     'Cheeseburger + French Fries (Large) + Classic Mojito.', 
     65000, 0, 'https://images.unsplash.com/photo-1561758033-d89a9ad46330?w=500&auto=format&fit=crop&q=80'),

    (34, 4, 'Combo Lavash Set', 'Комбо Lavash Set', 'Combo Lavash Set', 
     'Tovuqli Lavash + Kartoshka fri + Fanta Apelsin 0.5L.', 
     'Куриный лаваш + Картофель фри + Fanta Апельсин 0.5л.', 
     'Chicken Lavash + French Fries + Fanta Orange 0.5L.', 
     52000, 0, 'https://images.unsplash.com/photo-1626700051175-6818013e1d4f?w=500&auto=format&fit=crop&q=80'),

    (35, 4, 'Combo Sweet & Coffee', 'Комбо Sweet & Coffee', 'Combo Sweet & Coffee', 
     'Kapuchino Kofe + Nyu-York Chizkeyk + 2 ta shokoladli donut.', 
     'Кофе Капучино + Чизкейк Нью-Йорк + 2 шоколадных пончика.', 
     'Cappuccino Coffee + New York Cheesecake + 2x Chocolate Donuts.', 
     45000, 0, 'https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=500&auto=format&fit=crop&q=80')
]

cursor.executemany('''
    INSERT INTO menu (id, category_id, name, name_ru, name_en, description, description_ru, description_en, price, old_price, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', menu_items)

# ── PROMOTIONS (UZ, RU, EN) ──
promotions = [
    (1, 'Yozgi Super Chegirma', 'Летняя супер скидка', 'Summer Super Discount',
     'Fast Food taomlariga 15% chegirma!', 'Скидка 15% на все блюда фастфуда!', '15% discount on all Fast Food items!',
     15, '2026-08-31 23:59', 1, None, 1),
    (2, 'Salqin Ichimliklar Chegirmasi', 'Скидка на напитки', 'Cold Drinks Discount',
     'Barcha salqin ichimliklarga 20% chegirma!', 'Скидка 20% на все прохладительные напитки!', '20% discount on all cold beverages!',
     20, '2026-08-31 23:59', 2, None, 1)
]

cursor.executemany('''
    INSERT INTO promotions (id, title, title_ru, title_en, description, description_ru, description_en, discount_percent, end_date, category_id, menu_item_id, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', promotions)

conn.commit()
conn.close()
print("Multilingual baza (UZ, RU, EN) muvaffaqiyatli to'ldirildi!")
