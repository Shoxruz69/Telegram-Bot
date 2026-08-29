import aiosqlite
from contextlib import asynccontextmanager

DB_NAME = 'database/restaurant.db'
@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout=30000;")
        yield db

async def init_db():
    async with get_db() as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                phone TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                name_ru TEXT,
                name_en TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT,
                name_ru TEXT,
                name_en TEXT,
                description TEXT,
                description_ru TEXT,
                description_en TEXT,
                price INTEGER,
                old_price INTEGER DEFAULT 0,
                image_url TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                title_ru TEXT,
                title_en TEXT,
                description TEXT,
                description_ru TEXT,
                description_en TEXT,
                discount_percent INTEGER DEFAULT 0,
                end_date TEXT,
                category_id INTEGER,
                menu_item_id INTEGER,
                image_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id),
                FOREIGN KEY (menu_item_id) REFERENCES menu (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS cart (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (item_id) REFERENCES menu (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                daily_id INTEGER DEFAULT 1,
                user_id INTEGER,
                status TEXT DEFAULT 'Kutilmoqda',
                payment_method TEXT,
                receipt_image TEXT,
                total_amount INTEGER,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        # Buyurtma tarkibi uchun yangi jadval
        await db.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                menu_item_id INTEGER,
                name TEXT,
                price INTEGER,
                quantity INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_number TEXT,
                card_name TEXT,
                work_time_start TEXT DEFAULT '09:00',
                work_time_end TEXT DEFAULT '22:00',
                order_reset_hours INTEGER DEFAULT 24
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                discount_percent INTEGER NOT NULL DEFAULT 0,
                end_date TEXT,
                min_order_amount INTEGER DEFAULT 0,
                max_order_amount INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                times_used INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()
        
        # Populate some dummy categories and menu if empty
        async with db.execute('SELECT COUNT(*) FROM categories') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                await db.execute("INSERT INTO categories (name) VALUES ('Fast Food'), ('Ichimliklar'), ('Shirinliklar')")
                await db.commit()
                
        async with db.execute('SELECT COUNT(*) FROM menu') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                await db.executemany("INSERT INTO menu (category_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?)", [
                    (1, 'Lavash', 'Mol go''shtidan lavash', 25000, 'https://via.placeholder.com/150'),
                    (1, 'Gamburger', 'Katta gamburger', 20000, 'https://via.placeholder.com/150'),
                    (2, 'Coca Cola 1L', 'Muzdek kola', 10000, 'https://via.placeholder.com/150'),
                    (3, 'Medovik', 'Asalli tort', 15000, 'https://via.placeholder.com/150')
                ])
                await db.commit()

async def add_user(user_id, phone, lat, lon):
    async with get_db() as db:
        await db.execute('INSERT OR REPLACE INTO users (user_id, phone, latitude, longitude) VALUES (?, ?, ?, ?)', (user_id, phone, lat, lon))
        await db.commit()

async def get_user(user_id):
    async with get_db() as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_categories():
    async with get_db() as db:
        async with db.execute('SELECT * FROM categories') as cursor:
            return await cursor.fetchall()

async def get_menu_by_category(category_id):
    async with get_db() as db:
        async with db.execute('SELECT * FROM menu WHERE category_id = ?', (category_id,)) as cursor:
            return await cursor.fetchall()

async def get_item(item_id):
    async with get_db() as db:
        async with db.execute('SELECT * FROM menu WHERE id = ?', (item_id,)) as cursor:
            return await cursor.fetchone()

async def add_to_cart(user_id, item_id, quantity):
    async with get_db() as db:
        async with db.execute('SELECT quantity FROM cart WHERE user_id = ? AND item_id = ?', (user_id, item_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_quantity = row[0] + quantity
                await db.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND item_id = ?', (new_quantity, user_id, item_id))
            else:
                await db.execute('INSERT INTO cart (user_id, item_id, quantity) VALUES (?, ?, ?)', (user_id, item_id, quantity))
        await db.commit()

async def get_cart(user_id):
    async with get_db() as db:
        async with db.execute('''
            SELECT c.id, m.name, m.price, c.quantity, (m.price * c.quantity) as total 
            FROM cart c 
            JOIN menu m ON c.item_id = m.id 
            WHERE c.user_id = ?
        ''', (user_id,)) as cursor:
            return await cursor.fetchall()

async def clear_cart(user_id):
    async with get_db() as db:
        await db.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        await db.commit()

async def get_setting_card_number():
    async with get_db() as db:
        async with db.execute('SELECT card_number, card_name FROM settings LIMIT 1') as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return "8600 0000 0000 0000", "Ism Familiya"

async def create_order(user_id, payment_method, receipt_image=None):
    async with get_db() as db:
        # Hisoblash total_amount ni
        cart_items = await get_cart(user_id)
        total_amount = sum(item[4] for item in cart_items)
        
        await db.execute('''
            INSERT INTO orders (user_id, status, payment_method, receipt_image, total_amount) 
            VALUES (?, 'Kutilmoqda', ?, ?, ?)
        ''', (user_id, payment_method, receipt_image, total_amount))
        
        # Order_id ni olish
        async with db.execute('SELECT last_insert_rowid()') as cursor:
            order_id = (await cursor.fetchone())[0]
            
        await db.commit()
        return order_id
