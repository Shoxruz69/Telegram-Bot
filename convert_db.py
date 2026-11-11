import re

with open('c:/Telegram bot/database/sqlite_db.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace aiosqlite with asyncpg
content = content.replace("import aiosqlite", "import asyncpg\nimport os")

# Replace get_db
get_db_replacement = """
pg_pool = None

@asynccontextmanager
async def get_db():
    global pg_pool
    if not pg_pool:
        db_url = os.getenv("DATABASE_URL")
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        pg_pool = await asyncpg.create_pool(db_url)
    
    async with pg_pool.acquire() as conn:
        yield AsyncPGWrapper(conn)

class AsyncPGWrapper:
    def __init__(self, conn):
        self.conn = conn
        self.row_factory = None

    async def execute(self, query, params=None):
        if params is None:
            params = ()
        # Convert ? to $1, $2, etc.
        parts = query.split('?')
        q = parts[0]
        for i, p in enumerate(parts[1:], 1):
            q += f"${i}{p}"
            
        if q.strip().upper().startswith("SELECT"):
            records = await self.conn.fetch(q, *params)
            return AsyncPGCursor(records)
        elif "RETURNING" in q.upper():
            records = await self.conn.fetch(q, *params)
            return AsyncPGCursor(records)
        else:
            await self.conn.execute(q, *params)
            return AsyncPGCursor([])

    async def commit(self):
        pass

class AsyncPGCursor:
    def __init__(self, records):
        self.records = records
        self._idx = 0
    
    async def fetchone(self):
        if self._idx < len(self.records):
            res = self.records[self._idx]
            self._idx += 1
            return res
        return None
    
    async def fetchall(self):
        res = self.records[self._idx:]
        self._idx = len(self.records)
        return res
    
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
"""

# Extract the body of get_db from sqlite_db and replace it
content = re.sub(r'DB_NAME = .*?@asynccontextmanager\nasync def get_db\(\):.*?yield db', get_db_replacement, content, flags=re.DOTALL)

# Replace SQLite PRAGMAs in init_db
content = re.sub(r'async with db.execute\("PRAGMA table_info\((.*?)\)"\) as cursor:.*?await cursor\.fetchall\(\)', 
                 r'async with db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = \'\1\'") as cursor:\n                cols = [(0, row["column_name"]) for row in await cursor.fetchall()]', content, flags=re.DOTALL)

# Replace AUTOINCREMENT
content = content.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")

# Replace BOOLEAN DEFAULT 1
content = content.replace("BOOLEAN DEFAULT 1", "BOOLEAN DEFAULT TRUE")

# Replace DATETIME
content = content.replace("DATETIME DEFAULT CURRENT_TIMESTAMP", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

# Replace INSERT OR IGNORE INTO users
content = content.replace("INSERT OR IGNORE INTO users (user_id, tenant_id, phone, latitude, longitude)", "INSERT INTO users (user_id, tenant_id, phone, latitude, longitude) ON CONFLICT (user_id, tenant_id) DO NOTHING")
content = content.replace("INSERT OR IGNORE INTO users_migrated", "INSERT INTO users_migrated")

# Handle last_insert_rowid()
content = content.replace(
"""        await db.execute('''
            INSERT INTO bot_commands (tenant_id, command, description, reply_text, reply_image)
            VALUES (?, ?, ?, ?, ?)
        ''', (tenant_id, clean_cmd, description or '', reply_text, reply_image or ''))
        async with db.execute('SELECT last_insert_rowid()') as cursor:
            cmd_id = (await cursor.fetchone())[0]""",
"""        async with db.execute('''
            INSERT INTO bot_commands (tenant_id, command, description, reply_text, reply_image)
            VALUES (?, ?, ?, ?, ?) RETURNING id
        ''', (tenant_id, clean_cmd, description or '', reply_text, reply_image or '')) as cursor:
            cmd_id = (await cursor.fetchone())[0]"""
)

content = content.replace(
"""        await db.execute('''
            INSERT INTO orders (user_id, tenant_id, status, payment_method, receipt_image, total_amount) 
            VALUES (?, ?, 'Kutilmoqda', ?, ?, ?)
        ''', (user_id, tenant_id, payment_method, receipt_image, total_amount))
        
        async with db.execute('SELECT last_insert_rowid()') as cursor:
            order_id = (await cursor.fetchone())[0]""",
"""        async with db.execute('''
            INSERT INTO orders (user_id, tenant_id, status, payment_method, receipt_image, total_amount) 
            VALUES (?, ?, 'Kutilmoqda', ?, ?, ?) RETURNING id
        ''', (user_id, tenant_id, payment_method, receipt_image, total_amount)) as cursor:
            order_id = (await cursor.fetchone())[0]"""
)

# SQLite specific PRAGMA table_info loops
content = content.replace('async with db.execute(f"PRAGMA table_info({tbl})") as cursor:', 'async with db.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = \'{tbl}\'") as cursor:')

# The sqlite PRAGMA returns a tuple where index 1 is name. Our postgres query returns 'column_name'.
content = content.replace('cols = [row[1] for row in await cursor.fetchall()]', "cols = [row['column_name'] for row in await cursor.fetchall()]")

with open('c:/Telegram bot/database/postgres_db.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("postgres_db.py generated successfully.")
