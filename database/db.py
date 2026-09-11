import os

db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres"):
    from .postgres_db import *
else:
    from .sqlite_db import *
