import os
import json
import aiosqlite
from contextlib import asynccontextmanager
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'restaurant.db')
BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tenants_backup.json')

@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_NAME, timeout=60.0) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout=60000;")
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL DEFAULT 1,
                phone TEXT,
                latitude REAL,
                longitude REAL,
                UNIQUE (user_id, tenant_id)
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
                order_reset_hours INTEGER DEFAULT 24,
                welcome_message TEXT,
                welcome_image TEXT
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
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bot_commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_id INTEGER DEFAULT 1,
                command TEXT NOT NULL,
                description TEXT,
                reply_text TEXT NOT NULL,
                reply_image TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tenant_id, command)
            )
        ''')
        await db.commit()

        # 4. Migratsiyalar: users jadvalini multi-tenant qilish (user_id yagona PK bo'lmasligi kerak)
        try:
            async with db.execute("PRAGMA table_info(users)") as cursor:
                cols = await cursor.fetchall()
                # col: (cid, name, type, notnull, dflt_value, pk)
                is_old_pk = any(col[1] == 'user_id' and col[5] == 1 for col in cols) and not any(col[1] == 'id' for col in cols)
                if is_old_pk:
                    print("[Migration]: users jadvali multi-tenant sxemaga yangilanmoqda...")
                    await db.execute('''
                        CREATE TABLE users_migrated (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            tenant_id INTEGER NOT NULL DEFAULT 1,
                            phone TEXT,
                            latitude REAL,
                            longitude REAL,
                            UNIQUE (user_id, tenant_id)
                        )
                    ''')
                    await db.execute('''
                        INSERT OR IGNORE INTO users_migrated (user_id, tenant_id, phone, latitude, longitude)
                        SELECT user_id, COALESCE(tenant_id, 1), phone, latitude, longitude FROM users
                    ''')
                    await db.execute('DROP TABLE users')
                    await db.execute('ALTER TABLE users_migrated RENAME TO users')
                    await db.execute('CREATE INDEX IF NOT EXISTS idx_users_uid_tid ON users (user_id, tenant_id)')
                    await db.commit()
                    print("[Migration]: users jadvali muvaffaqiyatli ko'chirildi!")
        except Exception as uex:
            print(f"[Users migration error]: {uex}")

        # 5. Har bir jadvalda tenant_id borligini tekshirish
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
        # 6. Settings jadvalida welcome_message va welcome_image borligini tekshirish
        try:
            async with db.execute("PRAGMA table_info(settings)") as cursor:
                s_cols = [row[1] for row in await cursor.fetchall()]
                if 'welcome_message' not in s_cols:
                    await db.execute("ALTER TABLE settings ADD COLUMN welcome_message TEXT")
                if 'welcome_image' not in s_cols:
                    await db.execute("ALTER TABLE settings ADD COLUMN welcome_image TEXT")
                await db.commit()
        except Exception as sex:
            print(f"[Settings migration note]: {sex}")

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

        # 6.5. Barcha BOT_TOKEN_ bilan boshlanadigan Environment o'zgaruvchilarni qidirib avtomatik qo'shish
        for env_key, env_val in os.environ.items():
            if env_key.startswith("BOT_TOKEN_") and env_val.strip() and env_key != "BOT_TOKEN_":
                slug = env_key.replace("BOT_TOKEN_", "").strip().lower()
                if slug and slug != "express":
                    async with db.execute("SELECT COUNT(*) FROM tenants WHERE slug = ?", (slug,)) as cur:
                        if (await cur.fetchone())[0] == 0:
                            name = slug.capitalize() + " Cafe"
                            bot_username = f"@{name.replace(' ', '')}Bot"
                            admin_user = f"{slug}_admin"
                            admin_pw_hash = generate_password_hash("admin123")
                            
                            await db.execute('''
                                INSERT INTO tenants (name, slug, bot_token, bot_username, admin_telegram_id, admin_username, admin_password_hash, is_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (name, slug, env_val.strip(), bot_username, env_admin_id, admin_user, admin_pw_hash, 1))
                            await db.commit()
                            print(f"[Auto-Seed] {name} ({slug}) muhit o'zgaruvchisidan avtomatik qo'shildi!")
                        else:
                            # Agar mavjud bo'lsa, tokenini yangilash
                            await db.execute("UPDATE tenants SET bot_token = ?, is_active = 1 WHERE slug = ?", (env_val.strip(), slug))
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
        # 8. tenants_backup.json dan tiklash (agar Render konteyneri qayta ishga tushsa)
        if os.path.exists(BACKUP_FILE):
            try:
                with open(BACKUP_FILE, 'r', encoding='utf-8') as f:
                    bk_tenants = json.load(f)
                for bt in bk_tenants:
                    t_slug = bt.get('slug', '').strip().lower()
                    if not t_slug:
                        continue

                    env_token_key = f"BOT_TOKEN_{t_slug.upper()}"
                    env_token_val = os.getenv(env_token_key, "").strip()
                    if not env_token_val and (bt.get('id') == 1 or t_slug == 'express'):
                        env_token_val = os.getenv("BOT_TOKEN", "").strip()

                    bk_token = bt.get('bot_token', '').strip()
                    token_to_use = env_token_val or bk_token

                    async with db.execute("SELECT id, bot_token FROM tenants WHERE slug = ?", (t_slug,)) as cur:
                        row = await cur.fetchone()
                        if not row:
                            await db.execute('''
                                INSERT INTO tenants (name, slug, bot_token, bot_username, admin_telegram_id, admin_username, admin_password_hash, is_active)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                bt.get('name', 'Oshxona'),
                                t_slug,
                                token_to_use,
                                bt.get('bot_username', ''),
                                bt.get('admin_telegram_id', ''),
                                bt.get('admin_username', f"{t_slug}_admin"),
                                bt.get('admin_password_hash', generate_password_hash('admin123')),
                                1
                            ))
                            await db.commit()
                            print(f"[Backup restore]: Oshxona tiklandi: {bt.get('name')} ({t_slug})")
                        else:
                            curr_tok = row[1] or ''
                            is_curr_ph = any(ph in curr_tok.upper() for ph in ['YOUR_', '_HERE', 'PLACEHOLDER']) or not curr_tok
                            is_new_real = token_to_use and not any(ph in token_to_use.upper() for ph in ['YOUR_', '_HERE', 'PLACEHOLDER'])
                            if is_curr_ph and is_new_real:
                                await db.execute("UPDATE tenants SET bot_token = ?, is_active = 1 WHERE id = ?", (token_to_use, row[0]))
                                await db.commit()
                                print(f"[Backup restore]: Oshxona tokeni yangilandi ({t_slug})")
            except Exception as bke:
                print(f"[Backup restore error]: {bke}")

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
    token_clean = bot_token.strip()
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        # 1. Exact match (bo'sh joysiz)
        async with db.execute('SELECT * FROM tenants WHERE TRIM(bot_token) = ?', (token_clean,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
        # 2. Token prefix bo'yicha izlash (masalan bot_id:...)
        if ":" in token_clean:
            bot_prefix = token_clean.split(":")[0] + ":%"
            async with db.execute('SELECT * FROM tenants WHERE bot_token LIKE ?', (bot_prefix,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
        # Topilmasa None qaytarish (xato boshqa tenantga ulanmasligi uchun)
        return None

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
        async with db.execute("SELECT * FROM tenants WHERE is_active IN (1, '1', 'True', 'true', 1.0) OR is_active IS TRUE") as cursor:
            rows = await cursor.fetchall()
            tenants = [dict(r) for r in rows]
            for t in tenants:
                t_slug = str(t.get('slug', '')).strip().lower()
                tok = str(t.get('bot_token', '')).strip()
                if not tok or any(ph in tok.upper() for ph in ['YOUR_', '_HERE', 'PLACEHOLDER']):
                    env_tok = os.getenv(f"BOT_TOKEN_{t_slug.upper()}", "").strip()
                    if not env_tok and (t.get('id') == 1 or t_slug == 'express'):
                        env_tok = os.getenv("BOT_TOKEN", "").strip()
                    if env_tok and not any(ph in env_tok.upper() for ph in ['YOUR_', '_HERE']):
                        t['bot_token'] = env_tok
            return tenants

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
                await db.execute('INSERT OR IGNORE INTO users (user_id, tenant_id, phone, latitude, longitude) VALUES (?, ?, ?, ?, ?)', (user_id, tenant_id, phone or '', lat or 0.0, lon or 0.0))
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

async def get_welcome_settings(tenant_id=1):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT welcome_message, welcome_image FROM settings WHERE tenant_id = ? LIMIT 1', (tenant_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return row['welcome_message'], row['welcome_image']
            return None, None

async def backup_tenants_file():
    """Barcha oshxonalarni tenants_backup.json fayliga zaxiralash"""
    try:
        tenants = await get_all_tenants()
        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(tenants, f, ensure_ascii=False, indent=2)
        return True
    except Exception as ex:
        print(f"[backup_tenants_file error]: {ex}")
        return False

# --- Maxsus Bot Komandalari (Bot Commands) ---

async def get_all_custom_commands(tenant_id=1):
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM bot_commands WHERE tenant_id = ? ORDER BY id ASC', (tenant_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_custom_command(tenant_id, command_name):
    if not command_name:
        return None
    clean_cmd = command_name.strip().lstrip('/').lower()
    async with get_db() as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM bot_commands WHERE tenant_id = ? AND (command = ? OR command = ?)',
            (tenant_id, clean_cmd, f"/{clean_cmd}")
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_custom_command(tenant_id, command, description, reply_text, reply_image=None):
    clean_cmd = command.strip().lstrip('/').lower()
    async with get_db() as db:
        await db.execute('''
            INSERT INTO bot_commands (tenant_id, command, description, reply_text, reply_image)
            VALUES (?, ?, ?, ?, ?)
        ''', (tenant_id, clean_cmd, description or '', reply_text, reply_image or ''))
        async with db.execute('SELECT last_insert_rowid()') as cursor:
            cmd_id = (await cursor.fetchone())[0]
        await db.commit()
        return cmd_id

async def update_custom_command(cmd_id, tenant_id, command, description, reply_text, reply_image=None):
    clean_cmd = command.strip().lstrip('/').lower()
    async with get_db() as db:
        await db.execute('''
            UPDATE bot_commands 
            SET command = ?, description = ?, reply_text = ?, reply_image = ?
            WHERE id = ? AND tenant_id = ?
        ''', (clean_cmd, description or '', reply_text, reply_image or '', cmd_id, tenant_id))
        await db.commit()
        return True

async def delete_custom_command(cmd_id, tenant_id):
    async with get_db() as db:
        await db.execute('DELETE FROM bot_commands WHERE id = ? AND tenant_id = ?', (cmd_id, tenant_id))
        await db.commit()
        return True
