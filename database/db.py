import os
import aiosqlite
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant.db')

@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_NAME, timeout=30.0) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout=30000;")
        yield db

async def init_db():
    async with get_db() as db:
        # 1. Tenants (Oshxonalar) jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                bot_token TEXT UNIQUE NOT NULL,
                bot_username TEXT,
                admin_telegram_id TEXT,
                admin_username TEXT UNIQUE NOT NULL,
                admin_password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. Super Admins jadvali
        await db.execute('''
            CREATE TABLE IF NOT EXISTS super_admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 3. Asosiy jadvallar (tenant_id bilan)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                tenant_id INTEGER DEFAULT 1,
                phone TEXT,
                latitude REAL,
                longitude REAL
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER DEFAULT 1,
                name TEXT,
                name_ru TEXT,
                name_en TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER DEFAULT 1,
                category_id INTEGER,
                name TEXT,
                name_ru TEXT,
                name_en TEXT,
                description TEXT,
                description_ru TEXT,
                description_en TEXT,
                price INTEGER,
                old_price INTEGER DEFAULT 0,
                calories INTEGER DEFAULT 0,
                image_url TEXT,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promotions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER DEFAULT 1,
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
                tenant_id INTEGER DEFAULT 1,
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
                tenant_id INTEGER DEFAULT 1,
                daily_id INTEGER DEFAULT 1,
                user_id INTEGER,
                status TEXT DEFAULT 'Kutilmoqda',
                payment_method TEXT,
                receipt_image TEXT,
                total_amount INTEGER,
                address TEXT,
                promocode TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER DEFAULT 1,
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
                tenant_id INTEGER DEFAULT 1,
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
                tenant_id INTEGER DEFAULT 1,
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

        # 4. Migratsiyalar: har bir jadvalda tenant_id borligini tekshirish
        tables_to_check = ['users', 'categories', 'menu', 'promotions', 'cart', 'orders', 'order_items', 'settings', 'promocodes']
        for tbl in tables_to_check:
            try:
                async with db.execute(f"PRAGMA table_info({tbl})") as cursor:
                    cols = [row[1] for row in await cursor.fetchall()]
                    if 'tenant_id' not in cols:
                        await db.execute(f"ALTER TABLE {tbl} ADD COLUMN tenant_id INTEGER DEFAULT 1")
                        await db.execute(f"UPDATE {tbl} SET tenant_id = 1 WHERE tenant_id IS NULL")
            except Exception as ex:
                print(f"[Migration note: {tbl}]: {ex}")
        await db.commit()

        # 5. Standart Super Admin yaratish (agar yo'q bo'lsa)
        async with db.execute("SELECT COUNT(*) FROM super_admins") as cursor:
            sa_count = (await cursor.fetchone())[0]
            if sa_count == 0:
                default_sa_hash = generate_password_hash("admin777")
                await db.execute(
                    "INSERT INTO super_admins (username, password_hash) VALUES (?, ?)",
                    ("superadmin", default_sa_hash)
                )
                await db.commit()

        # 6. Standart Tenant #1 yaratish (Cafe Express / Dili Cafe - mavjud .env token bilan)
        env_token = os.getenv("BOT_TOKEN", "").strip()
        env_admin_id = os.getenv("ADMIN_ID", "").strip()

        async with db.execute("SELECT COUNT(*) FROM tenants") as cursor:
            t_count = (await cursor.fetchone())[0]
            if t_count == 0:
                t_token = env_token if env_token else "YOUR_BOT_TOKEN_HERE"
                t_admin_id = env_admin_id if env_admin_id else "YOUR_ADMIN_ID_HERE"
                default_tenant_hash = generate_password_hash("admin123")
                await db.execute('''
                    INSERT INTO tenants (id, name, slug, bot_token, bot_username, admin_telegram_id, admin_username, admin_password_hash, is_active)
                    VALUES (1, 'Cafe Express', 'express', ?, '@CafeExpressBot', ?, 'admin', ?, 1)
                ''', (t_token, t_admin_id, default_tenant_hash))
                await db.commit()
            else:
                # Agar bazada bot_token placeholder bo'lsa va env da haqiqiy token bo'lsa - avtomatik yangilash
                if env_token and env_token != "YOUR_BOT_TOKEN_HERE":
                    await db.execute("""
                        UPDATE tenants 
                        SET bot_token = ?, is_active = 1 
                        WHERE id = 1 AND (bot_token = 'YOUR_BOT_TOKEN_HERE' OR bot_token = '' OR bot_token IS NULL)
                    """, (env_token,))
                    await db.commit()
                if env_admin_id and env_admin_id != "YOUR_ADMIN_ID_HERE":
                    await db.execute("""
                        UPDATE tenants 
                        SET admin_telegram_id = ? 
                        WHERE id = 1 AND (admin_telegram_id = 'YOUR_ADMIN_ID_HERE' OR admin_telegram_id = '' OR admin_telegram_id IS NULL)
                    """, (env_admin_id,))
                    await db.commit()

        # 7. Mavjud kategoriyalar yoki menyu bo'sh bo'lsa boshlang'ich ma'lumotlar qo'shish
        async with db.execute('SELECT COUNT(*) FROM categories WHERE tenant_id = 1') as cursor:
            count = (await cursor.fetchone())[0]
            if count == 0:
                await db.execute("INSERT INTO categories (tenant_id, name) VALUES (1, 'Fast Food'), (1, 'Ichimliklar'), (1, 'Shirinliklar')")
                await db.commit()
                
        async with db.execute('SELECT COUNT(*) FROM menu WHERE tenant_id = 1') as cursor:
            count = (await cursor.fetchone())[0]
            if count == 0:
                await db.executemany("INSERT INTO menu (tenant_id, category_id, name, description, price, image_url) VALUES (1, ?, ?, ?, ?, ?)", [
                    (1, 'Lavash', 'Mol go''shtidan lavash', 25000, 'https://via.placeholder.com/150'),
                    (1, 'Gamburger', 'Katta gamburger', 20000, 'https://via.placeholder.com/150'),
                    (2, 'Coca Cola 1L', 'Muzdek kola', 10000, 'https://via.placeholder.com/150'),
                    (3, 'Medovik', 'Asalli tort', 15000, 'https://via.placeholder.com/150')
                ])
                await db.commit()

# --- Tenant & SuperAdmin Helper Funksiyalari ---

async def get_tenant_by_id(tenant_id):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tenants WHERE id = ?', (tenant_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_tenant_by_slug(slug):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tenants WHERE slug = ?', (slug.lower().strip(),)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_tenant_by_bot_token(bot_token):
    if not bot_token:
        return None
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tenants WHERE bot_token = ?', (bot_token.strip(),)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
        # Fallback: agar topilmasa (masalan bot_token .env dan olingan bo'lsa), id=1 dagi birinchi tenantni qaytarish
        async with db.execute('SELECT * FROM tenants WHERE id = 1') as cursor:
            row1 = await cursor.fetchone()
            return dict(row1) if row1 else None

async def get_tenant_by_admin_username(username):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tenants WHERE admin_username = ?', (username.strip(),)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_super_admin(username):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM super_admins WHERE username = ?', (username.strip(),)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_all_active_tenants():
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM tenants WHERE is_active = 1 OR is_active = '1' OR is_active = 1.0") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_all_tenants():
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM tenants ORDER BY id DESC') as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

# --- Tenant-Aware Operatsiyalar ---

async def add_user(user_id, phone, lat, lon, tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT phone, latitude, longitude FROM users WHERE user_id = ? AND tenant_id = ?', (user_id, tenant_id)) as cursor:
            existing = await cursor.fetchone()
            if existing:
                final_phone = phone if phone else existing[0]
                final_lat = lat if (lat and lat != 0.0) else existing[1]
                final_lon = lon if (lon and lon != 0.0) else existing[2]
                await db.execute('UPDATE users SET phone = ?, latitude = ?, longitude = ? WHERE user_id = ? AND tenant_id = ?', (final_phone, final_lat, final_lon, user_id, tenant_id))
            else:
                await db.execute('INSERT INTO users (user_id, tenant_id, phone, latitude, longitude) VALUES (?, ?, ?, ?, ?)', (user_id, tenant_id, phone or '', lat or 0.0, lon or 0.0))
        await db.commit()

async def get_user(user_id, tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT * FROM users WHERE user_id = ? AND tenant_id = ?', (user_id, tenant_id)) as cursor:
            return await cursor.fetchone()

async def get_categories(tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT * FROM categories WHERE tenant_id = ?', (tenant_id,)) as cursor:
            return await cursor.fetchall()

async def get_menu_by_category(category_id, tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT * FROM menu WHERE category_id = ? AND tenant_id = ?', (category_id, tenant_id)) as cursor:
            return await cursor.fetchall()

async def get_item(item_id, tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT * FROM menu WHERE id = ? AND tenant_id = ?', (item_id, tenant_id)) as cursor:
            return await cursor.fetchone()

async def add_to_cart(user_id, item_id, quantity, tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT quantity FROM cart WHERE user_id = ? AND item_id = ? AND tenant_id = ?', (user_id, item_id, tenant_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                new_quantity = row[0] + quantity
                await db.execute('UPDATE cart SET quantity = ? WHERE user_id = ? AND item_id = ? AND tenant_id = ?', (new_quantity, user_id, item_id, tenant_id))
            else:
                await db.execute('INSERT INTO cart (user_id, tenant_id, item_id, quantity) VALUES (?, ?, ?, ?)', (user_id, tenant_id, item_id, quantity))
        await db.commit()

async def get_cart(user_id, tenant_id=1):
    async with get_db() as db:
        async with db.execute('''
            SELECT c.id, m.name, m.price, c.quantity, (m.price * c.quantity) as total 
            FROM cart c 
            JOIN menu m ON c.item_id = m.id 
            WHERE c.user_id = ? AND c.tenant_id = ?
        ''', (user_id, tenant_id)) as cursor:
            return await cursor.fetchall()

async def clear_cart(user_id, tenant_id=1):
    async with get_db() as db:
        await db.execute('DELETE FROM cart WHERE user_id = ? AND tenant_id = ?', (user_id, tenant_id))
        await db.commit()

async def get_setting_card_number(tenant_id=1):
    async with get_db() as db:
        async with db.execute('SELECT card_number, card_name FROM settings WHERE tenant_id = ? LIMIT 1', (tenant_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            return "8600 0000 0000 0000", "Ism Familiya"

async def create_order(user_id, payment_method, receipt_image=None, tenant_id=1):
    async with get_db() as db:
        cart_items = await get_cart(user_id, tenant_id)
        total_amount = sum(item[4] for item in cart_items)
        
        await db.execute('''
            INSERT INTO orders (user_id, tenant_id, status, payment_method, receipt_image, total_amount) 
            VALUES (?, ?, 'Kutilmoqda', ?, ?, ?)
        ''', (user_id, tenant_id, payment_method, receipt_image, total_amount))
        
        async with db.execute('SELECT last_insert_rowid()') as cursor:
            order_id = (await cursor.fetchone())[0]
            
        await db.commit()
        return order_id
