import os
import requests
import json
import threading
import uuid
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload, subqueryload
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from markupsafe import Markup
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-restaurant-key'
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

from sqlalchemy import event
from sqlalchemy.engine import Engine

# Baza fayli joylashgan manzil
db_path = os.path.join(os.path.dirname(__file__), 'database', 'restaurant.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}?timeout=30'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'timeout': 30}}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()
    except Exception as e:
        print("[SQLite Pragma error]:", e)

db = SQLAlchemy(app)

# --- Ma'lumotlar bazasi modellari (SQLAlchemy) ---

class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    bot_token = db.Column(db.String(100), unique=True, nullable=False)
    bot_username = db.Column(db.String(100))
    admin_telegram_id = db.Column(db.String(50))
    admin_username = db.Column(db.String(50), unique=True, nullable=False)
    admin_password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.admin_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.admin_password_hash, password)

    def __repr__(self):
        return f"<Tenant {self.name} ({self.slug})>"

class SuperAdmin(db.Model):
    __tablename__ = 'super_admins'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<SuperAdmin {self.username}>"

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, default=1)
    phone = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __repr__(self):
        return f"<User {self.phone}>"

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    name = db.Column(db.String(100))
    name_ru = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    menus = db.relationship('Menu', backref='category', lazy=True)

    def __repr__(self):
        return self.name

class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String(100))
    name_ru = db.Column(db.String(100))
    name_en = db.Column(db.String(100))
    description = db.Column(db.Text)
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    price = db.Column(db.Integer)
    old_price = db.Column(db.Integer, default=0) # Eski narx (ustidan chizilgan)
    calories = db.Column(db.Integer, default=0) # Kaloriya (kkal)
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return self.name

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    quantity = db.Column(db.Integer)
    user = db.relationship('User', backref='cart_items')
    item = db.relationship('Menu', backref='cart_entries')

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    card_number = db.Column(db.String(100))
    card_name = db.Column(db.String(100))
    work_time_start = db.Column(db.String(10), default="09:00")
    work_time_end = db.Column(db.String(10), default="22:00")
    order_reset_hours = db.Column(db.Integer, default=24) # 24: Har 24 soatda 1-dan boshlanadi, 12: Har 12 soatda, 0: Reset o'chirilgan

    def __repr__(self):
        return f"Karta: {self.card_number} ({self.card_name})"

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    title = db.Column(db.String(200), nullable=False)
    title_ru = db.Column(db.String(200))
    title_en = db.Column(db.String(200))
    description = db.Column(db.Text)
    description_ru = db.Column(db.Text)
    description_en = db.Column(db.Text)
    discount_percent = db.Column(db.Integer, default=0)
    end_date = db.Column(db.String(100)) # Tugash vaqti
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu.id'), nullable=True)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    category = db.relationship('Category', backref='promotions')
    menu_item = db.relationship('Menu', backref='promotions')

    def __repr__(self):
        return f"Aksiya: {self.title}"

class PromoCode(db.Model):
    __tablename__ = 'promocodes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    code = db.Column(db.String(50), nullable=False)
    discount_percent = db.Column(db.Integer, nullable=False, default=0)
    end_date = db.Column(db.String(100), nullable=True) # Tugash vaqti masalan: '2026-12-31 23:59'
    min_order_amount = db.Column(db.Integer, default=0) # Minimal buyurtma summasi
    max_order_amount = db.Column(db.Integer, default=0) # Maksimal buyurtma summasi
    is_active = db.Column(db.Boolean, default=True)
    times_used = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f"Promokod: {self.code} (-{self.discount_percent}%)"

class OrderItem(db.Model):
    """Buyurtma tarkibidagi har bir mahsulot"""
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    menu_item_id = db.Column(db.Integer)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.name} x{self.quantity}"

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tenant_id = db.Column(db.Integer, default=1)
    daily_id = db.Column(db.Integer, default=1) # Har kunlik/soatlik 1, 2, 3... tartib raqam
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    status = db.Column(db.String(50), default="Kutilmoqda")
    payment_method = db.Column(db.String(50))
    receipt_image = db.Column(db.String(500))
    total_amount = db.Column(db.Integer)
    address = db.Column(db.String(500))
    promocode = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"Buyurtma #{self.daily_id or self.id} - {self.status}"

# --- Jadvallarni yaratish va Auto-migration ---
with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        
        # Settings migration
        settings_cols = [col['name'] for col in inspector.get_columns('settings')]
        if 'work_time_start' not in settings_cols:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN work_time_start VARCHAR(10) DEFAULT '09:00'"))
        if 'work_time_end' not in settings_cols:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN work_time_end VARCHAR(10) DEFAULT '22:00'"))
        if 'order_reset_hours' not in settings_cols:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN order_reset_hours INTEGER DEFAULT 24"))

        # Orders migration
        orders_cols = [col['name'] for col in inspector.get_columns('orders')]
        if 'daily_id' not in orders_cols:
            db.session.execute(text("ALTER TABLE orders ADD COLUMN daily_id INTEGER DEFAULT 1"))
        if 'promocode' not in orders_cols:
            db.session.execute(text("ALTER TABLE orders ADD COLUMN promocode VARCHAR(50)"))
            
        # Categories migration
        cat_cols = [col['name'] for col in inspector.get_columns('categories')]
        if 'name_ru' not in cat_cols:
            db.session.execute(text("ALTER TABLE categories ADD COLUMN name_ru VARCHAR(100)"))
        if 'name_en' not in cat_cols:
            db.session.execute(text("ALTER TABLE categories ADD COLUMN name_en VARCHAR(100)"))

        # Menu migration
        menu_cols = [col['name'] for col in inspector.get_columns('menu')]
        if 'old_price' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN old_price INTEGER DEFAULT 0"))
        if 'calories' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN calories INTEGER DEFAULT 0"))
        if 'name_ru' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN name_ru VARCHAR(100)"))
        if 'name_en' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN name_en VARCHAR(100)"))
        if 'description_ru' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN description_ru TEXT"))
        if 'description_en' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN description_en TEXT"))

        # Promotions migration
        promo_cols = [col['name'] for col in inspector.get_columns('promotions')]
        if 'end_date' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN end_date VARCHAR(100)"))
        if 'category_id' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN category_id INTEGER"))
        if 'menu_item_id' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN menu_item_id INTEGER"))
        if 'title_ru' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN title_ru VARCHAR(200)"))
        if 'title_en' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN title_en VARCHAR(200)"))
        if 'description_ru' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN description_ru TEXT"))
        if 'description_en' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN description_en TEXT"))

        # Promocodes migration
        promocodes_cols = [col['name'] for col in inspector.get_columns('promocodes')]
        if 'end_date' not in promocodes_cols:
            db.session.execute(text("ALTER TABLE promocodes ADD COLUMN end_date VARCHAR(100)"))
        if 'min_order_amount' not in promocodes_cols:
            db.session.execute(text("ALTER TABLE promocodes ADD COLUMN min_order_amount INTEGER DEFAULT 0"))
        if 'max_order_amount' not in promocodes_cols:
            db.session.execute(text("ALTER TABLE promocodes ADD COLUMN max_order_amount INTEGER DEFAULT 0"))

        # Multi-tenant migration
        for tbl in ['users', 'categories', 'menu', 'promotions', 'cart', 'orders', 'order_items', 'settings', 'promocodes']:
            try:
                tbl_cols = [col['name'] for col in inspector.get_columns(tbl)]
                if 'tenant_id' not in tbl_cols:
                    db.session.execute(text(f"ALTER TABLE {tbl} ADD COLUMN tenant_id INTEGER DEFAULT 1"))
                    db.session.execute(text(f"UPDATE {tbl} SET tenant_id = 1 WHERE tenant_id IS NULL"))
            except Exception as tex:
                print(f"[tenant_id migration {tbl}]:", tex)
        
        db.session.commit()

        # Seed SuperAdmin if empty
        try:
            if SuperAdmin.query.count() == 0:
                sa = SuperAdmin(username='superadmin')
                sa.set_password('admin777')
                db.session.add(sa)
                db.session.commit()
                print("[SuperAdmin seeded]: superadmin / admin777")
        except Exception as sae:
            print("[SuperAdmin seed error]:", sae)

        # Seed Tenant #1 (Cafe Express) or sync with env
        try:
            env_token = os.getenv("BOT_TOKEN", "").strip()
            env_admin_id = os.getenv("ADMIN_ID", "").strip()
            if Tenant.query.count() == 0:
                t1 = Tenant(
                    id=1,
                    name="Cafe Express",
                    slug="express",
                    bot_token=env_token or "YOUR_BOT_TOKEN_HERE",
                    bot_username="@CafeExpressBot",
                    admin_telegram_id=env_admin_id,
                    admin_username="admin",
                    is_active=True
                )
                t1.set_password("admin123")
                db.session.add(t1)
                db.session.commit()
                print("[Tenant 1 seeded]: Cafe Express (admin / admin123)")
            else:
                t1 = Tenant.query.get(1)
                if t1:
                    if env_token and env_token != "YOUR_BOT_TOKEN_HERE" and (not t1.bot_token or t1.bot_token == "YOUR_BOT_TOKEN_HERE"):
                        t1.bot_token = env_token
                        t1.is_active = True
                        db.session.commit()
                        print(f"[Tenant 1 token auto-synced from env]: {env_token[:8]}...")
                    if env_admin_id and env_admin_id != "YOUR_ADMIN_ID_HERE" and (not t1.admin_telegram_id or t1.admin_telegram_id == "YOUR_ADMIN_ID_HERE"):
                        t1.admin_telegram_id = env_admin_id
                        db.session.commit()
        except Exception as te:
            print("[Tenant seed error]:", te)

        # Seed initial sample promo code if table is empty
        try:
            if PromoCode.query.count() == 0:
                db.session.add(PromoCode(code='696JF', discount_percent=3, is_active=True, tenant_id=1))
                db.session.commit()
        except Exception as pe:
            print("[Promo seed error]:", pe)

        # Existing buyurtmalarga order_reset_hours sozlamasiga ko'ra daily_id berish
        def recalculate_daily_ids():
            try:
                setting_obj = Setting.query.first()
                rh = getattr(setting_obj, 'order_reset_hours', 24)
                if rh is None:
                    rh = 24

                orders_list = Order.query.order_by(Order.id.asc()).all()
                if not orders_list:
                    return

                prev_dt = None
                curr_daily_id = 0

                for o in orders_list:
                    dt_val = None
                    if o.created_at:
                        if isinstance(o.created_at, str):
                            try:
                                dt_val = datetime.strptime(o.created_at.split('.')[0], "%Y-%m-%d %H:%M:%S")
                            except:
                                dt_val = None
                        elif isinstance(o.created_at, datetime):
                            dt_val = o.created_at

                    if rh == 0:
                        curr_daily_id += 1
                        o.daily_id = curr_daily_id
                    else:
                        if prev_dt is None or dt_val is None:
                            curr_daily_id = 1
                        else:
                            diff_h = (dt_val - prev_dt).total_seconds() / 3600.0
                            if diff_h >= rh:
                                curr_daily_id = 1
                            else:
                                curr_daily_id += 1
                        o.daily_id = curr_daily_id

                    if dt_val:
                        prev_dt = dt_val

                db.session.commit()
            except Exception as ex:
                print(f"[recalculate_daily_ids error]: {ex}")

        recalculate_daily_ids()
    except Exception as e:
        print(f"[Auto-migration error]: {e}")


def check_promocode_validity(promo, order_amount=0):
    """
    Promokodning faolligi, muddati va buyurtma summasi chegaralarini tekshiradi.
    Qaytadi: (is_valid: bool, error_message: str or None)
    """
    if not promo or not promo.is_active:
        return False, "Promokod mavjud emas yoki nofaol!"

    # 1. Muddat tekshiruvi (end_date)
    if getattr(promo, 'end_date', None):
        end_str = str(promo.end_date).strip()
        if end_str:
            try:
                tz = timezone(timedelta(hours=5))
                now_tashkent = datetime.now(tz)
                clean_dt = end_str.replace('T', ' ')
                if len(clean_dt) == 10:
                    clean_dt += " 23:59"
                end_dt = datetime.strptime(clean_dt[:16], "%Y-%m-%d %H:%M").replace(tzinfo=tz)
                if now_tashkent > end_dt:
                    return False, "Promokod amal qilish muddati tugagan!"
            except Exception as e:
                print(f"[Promo date parse error]: {e}")

    # 2. Minimal buyurtma summasi
    min_amount = getattr(promo, 'min_order_amount', 0) or 0
    max_amount = getattr(promo, 'max_order_amount', 0) or 0

    if order_amount and order_amount > 0:
        if min_amount > 0 and order_amount < min_amount:
            formatted_min = f"{min_amount:,}".replace(',', ' ')
            return False, f"Ushbu promokod faqat {formatted_min} so'mdan yuqori buyurtmalar uchun amal qiladi!"

        # 3. Maksimal buyurtma summasi
        if max_amount > 0 and order_amount > max_amount:
            formatted_max = f"{max_amount:,}".replace(',', ' ')
            return False, f"Ushbu promokod maksimal {formatted_max} so'mgacha bo'lgan buyurtmalar uchun amal qiladi!"

    return True, None


def broadcast_to_users(text, photo_url_or_path=None, parse_mode='HTML', tenant_id=None):
    """
    Bot foydalanuvchilariga (User va Order jadvalidagi barcha mijozlarga) fonda reklama xabarini yuboradi.
    """
    def send_broadcast_worker():
        with app.app_context():
            t_obj = None
            if tenant_id:
                t_obj = Tenant.query.get(tenant_id)
            if not t_obj:
                t_obj = Tenant.query.first()

            bot_token = t_obj.bot_token if (t_obj and t_obj.bot_token) else os.getenv("BOT_TOKEN")
            if not bot_token:
                print("[Broadcast warning]: BOT_TOKEN sozlanmagan!")
                return

            t_id = t_obj.id if t_obj else 1
            target_ids = set()

            # 1. User jadvalidan barcha foydalanuvchilar
            try:
                users = User.query.filter(User.user_id.isnot(None), User.user_id > 1000, User.tenant_id == t_id).all()
                for u in users:
                    target_ids.add(int(u.user_id))
            except Exception as e:
                print(f"[Broadcast users query error]: {e}")

            # 2. Order jadvalidan barcha mijozlar
            try:
                orders = Order.query.filter(Order.user_id.isnot(None), Order.user_id > 1000, Order.tenant_id == t_id).all()
                for o in orders:
                    target_ids.add(int(o.user_id))
            except Exception as e:
                print(f"[Broadcast orders query error]: {e}")

            # 3. Admin ID
            admin_id = t_obj.admin_telegram_id if (t_obj and t_obj.admin_telegram_id) else os.getenv("ADMIN_ID")
            if admin_id and str(admin_id).isdigit() and int(admin_id) > 1000:
                target_ids.add(int(admin_id))

            print(f"[Broadcast tenant={t_id}]: Jami {len(target_ids)} ta mijozga reklama yuborilmoqda: {target_ids}")

            # Mini App ochish tugmasi
            raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
            web_app_url = raw_url.strip() if raw_url else ""
            if web_app_url and not web_app_url.startswith("http"):
                web_app_url = f"https://{web_app_url}"
            if web_app_url:
                web_app_url = f"{web_app_url.rstrip('/')}/webapp"
                if t_obj and t_obj.slug:
                    web_app_url += f"?tenant={t_obj.slug}"

            reply_markup = None
            if web_app_url:
                reply_markup = {
                    "inline_keyboard": [[
                        {"text": "🍔 Mini App ni ochish", "web_app": {"url": web_app_url}}
                    ]]
                }

            sent_count = 0
            for chat_id in target_ids:
                try:
                    if photo_url_or_path:
                        if str(photo_url_or_path).startswith(('http://', 'https://')):
                            payload = {
                                'chat_id': chat_id,
                                'photo': photo_url_or_path,
                                'caption': text,
                                'parse_mode': parse_mode
                            }
                            if reply_markup:
                                payload['reply_markup'] = json.dumps(reply_markup)
                            r = requests.post(
                                f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                                data=payload,
                                timeout=8
                            )
                            if r.status_code == 200:
                                sent_count += 1
                                print(f"[Broadcast OK] chat_id={chat_id} ga rasm bilan yetkazildi")
                            else:
                                print(f"[Broadcast fail] chat_id={chat_id} status={r.status_code} res={r.text[:120]}")
                        else:
                            local_photo = photo_url_or_path
                            if not os.path.isabs(local_photo):
                                local_photo = os.path.join(app.root_path, 'static', 'uploads', local_photo)
                            if os.path.exists(local_photo):
                                with open(local_photo, 'rb') as photo:
                                    payload = {
                                        'chat_id': chat_id,
                                        'caption': text,
                                        'parse_mode': parse_mode
                                    }
                                    if reply_markup:
                                        payload['reply_markup'] = json.dumps(reply_markup)
                                    r = requests.post(
                                        f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                                        data=payload,
                                        files={'photo': photo},
                                        timeout=8
                                    )
                                    if r.status_code == 200:
                                        sent_count += 1
                                        print(f"[Broadcast OK] chat_id={chat_id} ga fayl bilan yetkazildi")
                                    else:
                                        print(f"[Broadcast fail] chat_id={chat_id} status={r.status_code} res={r.text[:120]}")
                            else:
                                payload = {
                                    'chat_id': chat_id,
                                    'text': text,
                                    'parse_mode': parse_mode
                                }
                                if reply_markup:
                                    payload['reply_markup'] = reply_markup
                                r = requests.post(
                                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                    json=payload,
                                    timeout=8
                                )
                                if r.status_code == 200:
                                    sent_count += 1
                                    print(f"[Broadcast OK] chat_id={chat_id} ga yetkazildi")
                                else:
                                    print(f"[Broadcast fail] chat_id={chat_id} status={r.status_code} res={r.text[:120]}")
                    else:
                        payload = {
                            'chat_id': chat_id,
                            'text': text,
                            'parse_mode': parse_mode
                        }
                        if reply_markup:
                            payload['reply_markup'] = reply_markup
                        r = requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json=payload,
                            timeout=8
                        )
                        if r.status_code == 200:
                            sent_count += 1
                            print(f"[Broadcast OK] chat_id={chat_id} ga yetkazildi")
                        else:
                            print(f"[Broadcast fail] chat_id={chat_id} status={r.status_code} res={r.text[:120]}")
                except Exception as e:
                    print(f"[Broadcast to user {chat_id} error]: {e}")

            print(f"[Broadcast completed]: {sent_count}/{len(target_ids)} mijozga muvaffaqiyatli yuborildi.")

    threading.Thread(target=send_broadcast_worker, daemon=True).start()


def translate_text(text, target_lang):
    """
    O'zbekcha matnni avtomatik ravishda rus (ru) yoki ingliz (en) tiliga tarjima qiladi.
    """
    if not text or not str(text).strip():
        return ""
    text_str = str(text).strip()
    # 1. Clients5 Google Translate API (Juda tez va ishonchli)
    try:
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=uz&tl={target_lang}&q={requests.utils.quote(text_str)}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=5)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and len(data) > 0 and data[0]:
                return str(data[0]).strip()
            elif isinstance(data, str) and data.strip():
                return data.strip()
    except Exception as e:
        pass

    # 2. Google GTX Translate Fallback
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            'client': 'gtx',
            'sl': 'uz',
            'tl': target_lang,
            'dt': 't',
            'q': text_str
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, params=params, headers=headers, timeout=5)
        res.encoding = 'utf-8'
        if res.status_code == 200:
            data = res.json()
            if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                translated = "".join([segment[0] for segment in data[0] if segment and len(segment) > 0 and segment[0]])
                if translated.strip():
                    return translated.strip()
    except Exception as e:
        pass

    return text_str


@app.route('/api/admin/translate', methods=['POST'])
def api_admin_translate():
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'success': False, 'error': 'Matn kiritilmadi'}), 400

    ru_trans = translate_text(text, 'ru')
    en_trans = translate_text(text, 'en')

    return jsonify({
        'success': True,
        'translations': {
            'ru': ru_trans,
            'en': en_trans
        }
    })


_geocode_cache = {}

@app.route('/api/reverse_geocode')
def api_reverse_geocode():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    lang = request.args.get('lang', 'uz')
    if not lat or not lon:
        return jsonify({'success': False, 'address': ''})

    try:
        cache_key = f"{round(float(lat), 4)},{round(float(lon), 4)},{lang}"
        if cache_key in _geocode_cache:
            return jsonify({'success': True, 'address': _geocode_cache[cache_key]})
    except Exception:
        pass

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'CafeExpressBot/2.0 (contact@bitepoint.uz)', 'Accept-Language': lang}
        res = requests.get(url, headers=headers, timeout=4)
        if res.status_code == 200:
            data = res.json()
            if data and 'address' in data:
                a = data['address']
                road = a.get('road') or a.get('pedestrian') or a.get('suburb') or a.get('neighbourhood') or a.get('residential') or ''
                district = a.get('city_district') or a.get('district') or a.get('county') or a.get('village') or a.get('hamlet') or ''
                city = a.get('city') or a.get('town') or a.get('municipality') or a.get('state') or ''
                
                parts = []
                if road: parts.append(road)
                if district and district != city: parts.append(district)
                if city: parts.append(city)
                clean_addr = ", ".join(parts) if parts else data.get('display_name', '')
                if clean_addr:
                    try:
                        _geocode_cache[cache_key] = clean_addr
                    except:
                        pass
                    return jsonify({'success': True, 'address': clean_addr})
    except Exception as e:
        print(f"[Reverse geocode note]: {e}")

    return jsonify({'success': False, 'address': f"GPS: {lat}, {lon}"})


# --- WebApp API ---
@app.route('/webapp')
def webapp():
    tenant_slug = request.args.get('tenant', '').strip()
    return render_template('webapp.html', tenant_slug=tenant_slug)

@app.route('/ping', methods=['GET', 'HEAD'])
@app.route('/health', methods=['GET', 'HEAD'])
def ping():
    return "OK", 200

def start_self_ping():
    def ping_worker():
        import time, urllib.request, ssl
        time.sleep(5)
        ssl_ctx = ssl._create_unverified_context()
        while True:
            raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
            if raw_url:
                raw_url = raw_url.strip().rstrip("/")
                if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
                    base_url = f"https://{raw_url}"
                else:
                    base_url = raw_url
                
                if base_url.endswith("/webapp"):
                    base_url = base_url[:-7]
                
                ping_url = f"{base_url}/ping"
                try:
                    req = urllib.request.Request(ping_url, headers={"User-Agent": "KeepAlive-Admin/1.0"})
                    urllib.request.urlopen(req, timeout=15, context=ssl_ctx)
                    print(f"[KeepAlive Admin] Ping muvaffaqiyatli: {ping_url}", flush=True)
                except Exception as e:
                    print(f"[KeepAlive Admin] Ping xatosi: {e}", flush=True)
            
            time.sleep(150)

    t = threading.Thread(target=ping_worker, daemon=True)
    t.start()

start_self_ping()

@app.route('/api/data')
def api_data():
    tenant_param = request.args.get('tenant', '').strip()
    tenant_obj = None
    if tenant_param:
        tenant_obj = Tenant.query.filter((Tenant.slug == tenant_param.lower()) | (Tenant.id == tenant_param)).first()
    if not tenant_obj:
        tenant_obj = Tenant.query.first()

    t_id = tenant_obj.id if tenant_obj else 1
    categories = Category.query.filter_by(tenant_id=t_id).all()
    menus = Menu.query.filter_by(tenant_id=t_id).all()
    setting = Setting.query.filter_by(tenant_id=t_id).first()
    promotions = Promotion.query.filter_by(tenant_id=t_id, is_active=True).all()
    
    user_id = request.args.get('user_id')
    user_data = None
    if user_id and str(user_id).isdigit():
        uid_int = int(user_id)
        if uid_int > 1000:
            try:
                u = User.query.filter_by(user_id=uid_int, tenant_id=t_id).first()
                if not u:
                    u = User(user_id=uid_int, tenant_id=t_id, phone="", latitude=0.0, longitude=0.0)
                    db.session.add(u)
                    db.session.commit()
                if u:
                    user_data = {
                        'phone': u.phone or '',
                        'latitude': u.latitude or 0,
                        'longitude': u.longitude or 0
                    }
            except Exception as e:
                print(f"[api_data user auto-register error]: {e}")

    return jsonify({
        'restaurant_name': tenant_obj.name if tenant_obj else "Cafe Express",
        'categories': [{
            'id': c.id, 
            'name': c.name,
            'name_ru': getattr(c, 'name_ru', None) or c.name,
            'name_en': getattr(c, 'name_en', None) or c.name
        } for c in categories],
        'menu': [{
            'id': m.id, 
            'category_id': m.category_id, 
            'name': m.name, 
            'name_ru': getattr(m, 'name_ru', None) or m.name,
            'name_en': getattr(m, 'name_en', None) or m.name,
            'description': m.description or '', 
            'description_ru': getattr(m, 'description_ru', None) or m.description or '',
            'description_en': getattr(m, 'description_en', None) or m.description or '',
            'price': m.price, 
            'old_price': getattr(m, 'old_price', 0) or 0,
            'calories': getattr(m, 'calories', 0) or 0,
            'image_url': m.image_url
        } for m in menus],
        'promotions': [{
            'id': p.id,
            'title': p.title,
            'title_ru': getattr(p, 'title_ru', None) or p.title,
            'title_en': getattr(p, 'title_en', None) or p.title,
            'description': p.description or '',
            'description_ru': getattr(p, 'description_ru', None) or p.description or '',
            'description_en': getattr(p, 'description_en', None) or p.description or '',
            'discount_percent': p.discount_percent,
            'end_date': p.end_date,
            'category_id': p.category_id,
            'menu_item_id': p.menu_item_id,
            'image_url': p.image_url
        } for p in promotions],
        'settings': {
            'card_number': setting.card_number if setting else "8600 0000 0000 0000",
            'card_name': setting.card_name if setting else (tenant_obj.name if tenant_obj else "Ism Familiya")
        },
        'user': user_data
    })

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """1-qadam: Buyurtmani tezda saqlash va javob qaytarish (UI qotib qolmaydi)"""
    try:
        data = None
        if request.is_json:
            data = request.get_json(silent=True)
        if not data:
            try:
                data = json.loads(request.data.decode('utf-8'))
            except:
                data = None
        if not data:
            data = request.form.to_dict()

        tenant_param = (data.get('tenant') if data else '') or request.args.get('tenant', '').strip()
        tenant_obj = None
        if tenant_param:
            tenant_obj = Tenant.query.filter((Tenant.slug == str(tenant_param).lower()) | (Tenant.id == tenant_param)).first()
        if not tenant_obj:
            tenant_obj = Tenant.query.first()
        tenant_id = tenant_obj.id if tenant_obj else 1

        # Ish vaqtini tekshirish
        setting = Setting.query.filter_by(tenant_id=tenant_id).first()
        if setting and getattr(setting, 'work_time_start', None) and getattr(setting, 'work_time_end', None):
            start = setting.work_time_start.strip() if setting.work_time_start else ""
            end = setting.work_time_end.strip() if setting.work_time_end else ""
            if start and end and (start != "00:00" or end != "00:00"):
                tz = timezone(timedelta(hours=5))
                now = datetime.now(tz)
                current_time_str = now.strftime("%H:%M")
                if start <= end:
                    if not (start <= current_time_str <= end):
                        return jsonify({'success': False, 'error': f"Ish vaqti tugadi! Bizning ish vaqtimiz {start} dan {end} gacha."})
                else:
                    if not (current_time_str >= start or current_time_str <= end):
                        return jsonify({'success': False, 'error': f"Ish vaqti tugadi! Bizning ish vaqtimiz {start} dan {end} gacha."})

        user_id = str(data.get('user_id', '')).strip()
        phone = str(data.get('phone', '')).strip()
        address = str(data.get('address', '')).strip()
        payment_method = str(data.get('payment_method', 'Naqd'))
        items_raw = data.get('items', '[]')
        latitude = data.get('latitude', 0)
        longitude = data.get('longitude', 0)

        # Agar user_id kelmagan yoki '0' bo'lsa, DB dan ushbu telefon raqamli foydalanuvchini izlaymiz
        if (not user_id or user_id == '0') and phone:
            found_u = User.query.filter(User.phone == phone, User.user_id != 0, User.tenant_id == tenant_id).first()
            if found_u:
                user_id = str(found_u.user_id)

        if not phone:
            return jsonify({'success': False, 'error': "Telefon raqam kiritilmagan!"})

        try:
            items = json.loads(items_raw) if isinstance(items_raw, str) else items_raw
        except:
            items = []

        if not items:
            return jsonify({'success': False, 'error': "Savat bo'sh!"})

        # Buyurtma tarkibini hisoblash
        total_amount = 0
        order_items_data = []
        order_text_items = ""
        active_promotions = Promotion.query.filter_by(tenant_id=tenant_id, is_active=True).all()

        for item in items:
            menu_item = Menu.query.filter_by(id=int(item['id']), tenant_id=tenant_id).first()
            if not menu_item:
                menu_item = Menu.query.get(int(item['id']))
            if menu_item:
                qty = int(item['qty'])
                price = menu_item.price
                old_price = getattr(menu_item, 'old_price', 0) or 0

                # Aksiya chegirmasini hisoblash
                best_discount = 0
                for p in active_promotions:
                    discount = p.discount_percent or 0
                    if discount <= 0:
                        continue
                    matches_item = p.menu_item_id and int(p.menu_item_id) == menu_item.id
                    matches_cat = p.category_id and int(p.category_id) == menu_item.category_id
                    is_gen = not p.category_id and not p.menu_item_id
                    if matches_item or matches_cat or is_gen:
                        if discount > best_discount:
                            best_discount = discount

                if best_discount > 0:
                    base = old_price if (old_price and old_price > price) else price
                    price = round(base * (1 - best_discount / 100.0))

                # Frontend payload price bilan solishtirish
                if 'price' in item and item['price']:
                    try:
                        payload_price = int(item['price'])
                        if 0 < payload_price < price:
                            price = payload_price
                    except:
                        pass

                subtotal = price * qty
                total_amount += subtotal
                order_items_data.append({
                    'menu_item_id': menu_item.id,
                    'name': menu_item.name,
                    'price': price,
                    'quantity': qty
                })
                order_text_items += f"• {menu_item.name} x{qty} = {subtotal:,} so'm\n"

        lat_val = float(latitude) if latitude else 0.0
        lon_val = float(longitude) if longitude else 0.0

        # Foydalanuvchini saqlash/yangilash
        try:
            parsed_uid = int(user_id) if (user_id and user_id.isdigit()) else 0
            if parsed_uid > 0:
                user_obj = User.query.filter_by(user_id=parsed_uid, tenant_id=tenant_id).first()
                if not user_obj:
                    user_obj = User(user_id=parsed_uid, tenant_id=tenant_id, phone=phone, latitude=lat_val, longitude=lon_val)
                    db.session.add(user_obj)
                else:
                    user_obj.phone = phone
                    user_obj.latitude = lat_val
                    user_obj.longitude = lon_val
        except Exception as e:
            print(f"[User save error]: {e}")

        receipts_dir = os.path.join(app.root_path, 'static', 'uploads', 'receipts')

        # Chek (Base64 formatda yuborilgan bo'lsa)
        receipt_filename = None
        receipt_base64 = data.get('receipt_base64')
        if payment_method == 'Karta' and receipt_base64:
            try:
                if "," in receipt_base64:
                    receipt_base64 = receipt_base64.split(",")[1]
                import base64
                file_data = base64.b64decode(receipt_base64)
                receipt_filename = str(uuid.uuid4())[:8] + "_karta.jpg"
                os.makedirs(receipts_dir, exist_ok=True)
                with open(os.path.join(receipts_dir, receipt_filename), 'wb') as f:
                    f.write(file_data)
            except Exception as e:
                print(f"[Base64 decode error]: {e}")

        # Setting-dan order_reset_hours ni olish (default 24 soat)
        reset_hours = getattr(setting, 'order_reset_hours', 24) if setting else 24
        if reset_hours is None:
            reset_hours = 24

        now_utc = datetime.utcnow()
        last_order = Order.query.filter_by(tenant_id=tenant_id).order_by(Order.id.desc()).first()

        if not last_order:
            next_daily_id = 1
        elif reset_hours == 0:
            next_daily_id = (getattr(last_order, 'daily_id', None) or last_order.id) + 1
        else:
            last_dt = getattr(last_order, 'created_at', None)
            if last_dt:
                if isinstance(last_dt, str):
                    try:
                        last_dt = datetime.strptime(last_dt.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    except:
                        last_dt = None

            if last_dt and isinstance(last_dt, datetime):
                diff_hours = (now_utc - last_dt).total_seconds() / 3600.0
                if diff_hours >= reset_hours:
                    next_daily_id = 1
                else:
                    next_daily_id = (getattr(last_order, 'daily_id', None) or last_order.id) + 1
            else:
                next_daily_id = (getattr(last_order, 'daily_id', None) or last_order.id) + 1

        # Promokodni hisoblash
        promocode_str = str(data.get('promocode', '')).strip().upper()
        applied_promo = None
        promo_discount_amount = 0
        if promocode_str:
            promo_obj = PromoCode.query.filter_by(tenant_id=tenant_id, code=promocode_str).first()
            if promo_obj:
                is_valid, _ = check_promocode_validity(promo_obj, total_amount)
                if is_valid and promo_obj.discount_percent > 0:
                    applied_promo = promo_obj
                    promo_discount_amount = round(total_amount * (promo_obj.discount_percent / 100.0))
                    total_amount = max(0, total_amount - promo_discount_amount)
                    promo_obj.times_used = (promo_obj.times_used or 0) + 1

        # Buyurtmani DB ga saqlash
        new_order = Order(
            tenant_id=tenant_id,
            daily_id=next_daily_id,
            user_id=int(user_id) if str(user_id).isdigit() else 0,
            status="Kutilmoqda",
            payment_method=payment_method,
            receipt_image=receipt_filename,
            total_amount=total_amount,
            address=address,
            promocode=applied_promo.code if applied_promo else None
        )
        db.session.add(new_order)
        db.session.flush()

        for oi in order_items_data:
            db.session.add(OrderItem(
                tenant_id=tenant_id,
                order_id=new_order.id,
                menu_item_id=oi['menu_item_id'],
                name=oi['name'],
                price=oi['price'],
                quantity=oi['quantity']
            ))

        db.session.commit()
        order_id = new_order.id
        order_no = new_order.daily_id or order_id

        # Admin va mijozga FONDA xabar yuborish (UI ni kuttiradigan narsa yo'q)
        promo_line = f"🎟️ Promokod: {applied_promo.code} (-{applied_promo.discount_percent}% / -{promo_discount_amount:,} so'm)\n" if applied_promo else ""
        restaurant_display = f"🍽️ {tenant_obj.name}\n" if tenant_obj else ""
        order_text = (
            f"🆕 YANGI BUYURTMA #{order_no}!\n"
            f"{restaurant_display}\n"
            f"👤 Mijoz: {phone}\n"
            f"📍 Manzil: {address}\n"
            f"💳 To'lov: {payment_method}\n"
            f"{promo_line}"
            f"🛒 Tarkib:\n{order_text_items}"
            f"💰 Jami: {total_amount:,} so'm\n"
        )

        def notify_all():
            bot_token = tenant_obj.bot_token if (tenant_obj and tenant_obj.bot_token) else os.getenv("BOT_TOKEN")
            admin_id = tenant_obj.admin_telegram_id if (tenant_obj and tenant_obj.admin_telegram_id) else os.getenv("ADMIN_ID")
            if not bot_token:
                print(f"[Notify warning]: Tenant {tenant_id} uchun BOT_TOKEN sozlanmagan!")
                return

            # Admin xabari
            if admin_id and admin_id not in ("YOUR_ADMIN_ID_HERE", "", None):
                try:
                    if receipt_filename:
                        photo_path = os.path.join(receipts_dir, receipt_filename)
                        if os.path.exists(photo_path):
                            with open(photo_path, 'rb') as photo:
                                requests.post(
                                    f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                                    data={'chat_id': admin_id, 'caption': order_text, 'parse_mode': 'HTML'},
                                    files={'photo': photo},
                                    timeout=12
                                )
                        else:
                            requests.post(
                                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                json={'chat_id': admin_id, 'text': order_text, 'parse_mode': 'HTML'},
                                timeout=12
                            )
                    else:
                        requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendMessage",
                            json={'chat_id': admin_id, 'text': order_text, 'parse_mode': 'HTML'},
                            timeout=12
                        )
                    if lat_val and lon_val and lat_val != 0.0:
                        requests.post(
                            f"https://api.telegram.org/bot{bot_token}/sendLocation",
                            json={'chat_id': admin_id, 'latitude': lat_val, 'longitude': lon_val},
                            timeout=12
                        )
                except Exception as e:
                    print(f"[Admin notify error]: {e}")

            # Mijoz xabari
            if user_id and str(user_id) not in ('0', '', 'None'):
                try:
                    user_msg = (
                        f"✅ Buyurtmangiz #{order_no} qabul qilindi!\n"
                        f"💰 Jami: {total_amount:,} so'm ({payment_method})\n"
                        f"⏳ Admin tasdiqlashi kutilmoqda..."
                    )
                    requests.post(
                        f"https://api.telegram.org/bot{bot_token}/sendMessage",
                        json={'chat_id': user_id, 'text': user_msg},
                        timeout=8
                    )
                except Exception as e:
                    print(f"[User notify error]: {e}")

        threading.Thread(target=notify_all, daemon=True).start()

        # DB ga yozilgandan so'ng DARHOL javob qaytariladi
        return jsonify({'success': True, 'order_id': order_no})
    except Exception as err:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': f"Xatolik: {str(err)}"})


@app.route('/api/upload_receipt/<int:order_id>', methods=['POST'])
def upload_receipt(order_id):
    """2-qadam: Karta to'lovi chekini alohida yuklash (FormData orqali)"""
    print(f"[upload_receipt] order_id={order_id}, files={list(request.files.keys())}, form={list(request.form.keys())}")
    
    order = Order.query.get(order_id)
    if not order:
        print(f"[upload_receipt] Buyurtma #{order_id} topilmadi")
        return jsonify({'success': False, 'error': 'Buyurtma topilmadi'})

    if 'receipt' not in request.files:
        print(f"[upload_receipt] 'receipt' yo'q. Mavjud: {list(request.files.keys())}")
        return jsonify({'success': False, 'error': 'receipt fayli topilmadi'})

    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Fayl tanlanmagan'})

    try:
        filename = str(uuid.uuid4())[:8] + "_" + secure_filename(file.filename or 'receipt.jpg')
        receipts_dir = os.path.join(app.root_path, 'static', 'uploads', 'receipts')
        os.makedirs(receipts_dir, exist_ok=True)
        file_path = os.path.join(receipts_dir, filename)
        file.save(file_path)
        print(f"[upload_receipt] Fayl saqlandi: {file_path}")
    except Exception as e:
        print(f"[upload_receipt] Fayl saqlashda xatolik: {e}")
        return jsonify({'success': False, 'error': str(e)})

    try:
        order.receipt_image = filename
        db.session.commit()
    except Exception as e:
        print(f"[upload_receipt] DB xatolik: {e}")
        return jsonify({'success': False, 'error': 'DB xatolik'})

    # Thread uchun ma'lumotlarni oldindan olamiz
    order_total = order.total_amount
    order_phone = order.user.phone if order.user else 'N/A'
    order_address = order.address
    tenant_id = order.tenant_id or 1
    tenant_obj = Tenant.query.get(tenant_id) if tenant_id else Tenant.query.first()
    bot_token = tenant_obj.bot_token if (tenant_obj and tenant_obj.bot_token) else os.getenv("BOT_TOKEN")
    admin_id = tenant_obj.admin_telegram_id if (tenant_obj and tenant_obj.admin_telegram_id) else os.getenv("ADMIN_ID")

    items_text = ""
    for oi in order.items:
        items_text += f"• {oi.name} x{oi.quantity} = {oi.price * oi.quantity:,} so'm\n"

    def send_receipt_to_admin():
        if not bot_token or not admin_id or admin_id in ("YOUR_ADMIN_ID_HERE", ""):
            return
        caption = (
            f"💳 KARTA TO'LOVI CHEKI\n"
            f"Buyurtma #{order_id}\n"
            f"📞 {order_phone}\n"
            f"📍 {order_address}\n\n"
            f"🛒 Tarkib:\n{items_text}"
            f"💰 Jami: {order_total:,} so'm"
        )
        try:
            with open(file_path, 'rb') as photo:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                    data={'chat_id': admin_id, 'caption': caption},
                    files={'photo': photo},
                    timeout=15
                )
            print(f"[upload_receipt] Chek adminga yuborildi")
        except Exception as e:
            print(f"[Receipt upload error]: {e}")

    threading.Thread(target=send_receipt_to_admin, daemon=True).start()
    return jsonify({'success': True})


# --- Bitepoint Order Notification Helper ---
def send_telegram_order_status_update(user_id, order_id, status, payment_method, total_amount, tenant_id=1):
    tenant = Tenant.query.get(tenant_id)
    bot_token = tenant.bot_token if (tenant and tenant.bot_token) else os.getenv("BOT_TOKEN")
    if not bot_token or not user_id:
        return
    payment = payment_method or "Naqd"
    total = total_amount or 0
    if status == 'Tasdiqlandi':
        msg = (
            f"✅ #{order_id}-raqamli buyurtmangiz TASDIQLANDI!\n\n"
            f"💳 To'lov turi: {payment}\n"
            f"💰 Jami: {total:,} so'm\n\n"
            f"🚚 Buyurtmangiz tez orada yetkazib beriladi. Rahmat! 🙏"
        )
    elif status == 'Tayyorlanmoqda':
        msg = (
            f"🔥 #{order_id}-raqamli buyurtmangiz tayyorlanmoqda!\n"
            f"Oshpazlarimiz taomingizni tayyorlashga kirishdi 👨‍🍳"
        )
    elif status == 'Tugatildi':
        msg = (
            f"🎉 #{order_id}-raqamli buyurtmangiz yetkazildi / tugatildi!\n"
            f"Yoqimli ishtaha! Bizni tanlaganingiz uchun rahmat! ❤️"
        )
    elif status == 'Bekor qilindi':
        msg = (
            f"❌ #{order_id}-raqamli buyurtmangiz BEKOR QILINDI!\n\n"
            f"Qo'shimcha ma'lumot uchun biz bilan bog'laning."
        )
    else:
        return

    def _worker():
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json={"chat_id": int(user_id), "text": msg},
                timeout=8
            )
            print(f"[Admin Notify] Status '{status}' -> user {user_id}: {resp.status_code}")
        except Exception as e:
            print("[Admin status notify error]:", e)

    threading.Thread(target=_worker, daemon=True).start()


# --- Auth & Session Helperlari ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            return redirect(url_for('login_view', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'super_admin':
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

def get_current_tenant():
    if session.get('user_type') == 'super_admin' and not session.get('tenant_id'):
        return Tenant.query.first()
    t_id = session.get('tenant_id')
    if t_id:
        t = Tenant.query.get(t_id)
        if t:
            return t
    return Tenant.query.first()

def get_current_tenant_id():
    t = get_current_tenant()
    return t.id if t else 1


# --- Auth Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        if session.get('user_type') == 'super_admin':
            return redirect('/superadmin')
        elif session.get('user_type') == 'tenant_admin':
            return redirect('/admin')
        return render_template('login.html')

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    username = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    if not username or not password:
        return jsonify({'success': False, 'error': 'Login va parolni kiriting!'}), 400

    # 1. Super Admin tekshiruvi
    sa = SuperAdmin.query.filter_by(username=username).first()
    if sa and sa.check_password(password):
        session.clear()
        session['user_type'] = 'super_admin'
        session['username'] = sa.username
        return jsonify({'success': True, 'redirect': '/superadmin', 'user_type': 'super_admin'})

    # 2. Oshxona Admin tekshiruvi
    t = Tenant.query.filter_by(admin_username=username).first()
    if t and t.check_password(password):
        if not t.is_active:
            return jsonify({'success': False, 'error': "Ushbu oshxona faoliyati to'xtatilgan yoki bloklangan!"}), 403
        session.clear()
        session['user_type'] = 'tenant_admin'
        session['tenant_id'] = t.id
        session['tenant_slug'] = t.slug
        session['tenant_name'] = t.name
        session['username'] = t.admin_username
        return jsonify({'success': True, 'redirect': '/admin', 'user_type': 'tenant_admin'})

    return jsonify({'success': False, 'error': 'Login yoki parol noto\'g\'ri!'}), 401


@app.route('/logout')
def logout_view():
    session.clear()
    return redirect('/login')


@app.route('/superadmin/exit-impersonate')
def exit_impersonate():
    if session.get('is_impersonating'):
        session.clear()
        session['user_type'] = 'super_admin'
        session['username'] = 'superadmin'
        return redirect('/superadmin')
    return redirect('/login')


# --- Super Admin Panel Routes & APIs ---

@app.route('/superadmin')
@super_admin_required
def super_admin_dashboard():
    return render_template('admin/super_admin.html')


@app.route('/api/superadmin/stats')
@super_admin_required
def api_superadmin_stats():
    total_tenants = Tenant.query.count()
    active_tenants = Tenant.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(Order.status.in_(['Tasdiqlandi', 'Tugatildi'])).scalar() or 0
    return jsonify({
        'success': True,
        'stats': {
            'total_tenants': total_tenants,
            'active_tenants': active_tenants,
            'total_orders': total_orders,
            'total_revenue': total_revenue
        }
    })


@app.route('/api/superadmin/tenants')
@super_admin_required
def api_superadmin_tenants():
    tenants = Tenant.query.order_by(Tenant.id.desc()).all()
    result = []
    for t in tenants:
        orders_count = Order.query.filter_by(tenant_id=t.id).count()
        rev = db.session.query(db.func.sum(Order.total_amount)).filter(Order.tenant_id == t.id, Order.status.in_(['Tasdiqlandi', 'Tugatildi'])).scalar() or 0
        created_str = t.created_at.strftime("%Y-%m-%d %H:%M") if t.created_at else ""
        result.append({
            'id': t.id,
            'name': t.name,
            'slug': t.slug,
            'bot_username': t.bot_username or '',
            'bot_token_masked': t.bot_token[:8] + "..." + t.bot_token[-4:] if len(t.bot_token) > 12 else "***",
            'admin_telegram_id': t.admin_telegram_id or '',
            'admin_username': t.admin_username,
            'is_active': bool(t.is_active),
            'orders_count': orders_count,
            'total_revenue': rev,
            'created_at': created_str
        })
    return jsonify({'success': True, 'tenants': result})


@app.route('/api/superadmin/verify-token', methods=['POST'])
@super_admin_required
def api_superadmin_verify_token():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    token = str(data.get('token', '')).strip()
    if not token:
        return jsonify({'success': False, 'error': 'Token kiritilmadi'}), 400
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8)
        res = r.json()
        if res.get('ok'):
            return jsonify({'success': True, 'bot': res.get('result')})
        else:
            return jsonify({'success': False, 'error': res.get('description', 'Yaroqsiz token')})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/superadmin/tenants/create', methods=['POST'])
@super_admin_required
def api_superadmin_tenants_create():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    name = str(data.get('name', '')).strip()
    slug = str(data.get('slug', '')).strip().lower()
    bot_token = str(data.get('bot_token', '')).strip()
    admin_telegram_id = str(data.get('admin_telegram_id', '')).strip()
    admin_username = str(data.get('admin_username', '')).strip()
    admin_password = str(data.get('admin_password', '')).strip()
    clone_menu = bool(data.get('clone_menu', True))

    if not name:
        return jsonify({'success': False, 'error': 'Oshxona nomi kiritilmadi!'}), 400
    if not bot_token:
        return jsonify({'success': False, 'error': 'Telegram bot tokeni kiritilmadi!'}), 400
    if not admin_username or not admin_password:
        return jsonify({'success': False, 'error': 'Admin logini va paroli kiritilmadi!'}), 400

    if not slug:
        slug = re.sub(r'[^a-zA-Z0-9_]', '', name.lower().replace(' ', '_'))[:20]

    # Unikallikni tekshirish
    if Tenant.query.filter_by(slug=slug).first():
        return jsonify({'success': False, 'error': f"'{slug}' identifikatori allaqachon mavjud!"}), 400
    if Tenant.query.filter_by(bot_token=bot_token).first():
        return jsonify({'success': False, 'error': "Ushbu bot tokeni allaqachon boshqa oshxonaga ulangan!"}), 400
    if Tenant.query.filter_by(admin_username=admin_username).first() or SuperAdmin.query.filter_by(username=admin_username).first():
        return jsonify({'success': False, 'error': f"'{admin_username}' logini allaqachon band!"}), 400

    # Telegram bot tokenini tekshirish va @username ni olish
    bot_username = ''
    try:
        r = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=8)
        res = r.json()
        if not res.get('ok'):
            return jsonify({'success': False, 'error': f"Telegram API xatosi: {res.get('description', 'Yaroqsiz token')}"}), 400
        raw_user = res.get('result', {}).get('username', '')
        if raw_user:
            bot_username = '@' + raw_user if not raw_user.startswith('@') else raw_user
    except Exception as te:
        return jsonify({'success': False, 'error': f"Telegram botini tekshirib bo'lmadi: {te}"}), 400

    # Yangi Tenant yaratish
    new_tenant = Tenant(
        name=name,
        slug=slug,
        bot_token=bot_token,
        bot_username=bot_username,
        admin_telegram_id=admin_telegram_id,
        admin_username=admin_username,
        is_active=True
    )
    new_tenant.set_password(admin_password)
    db.session.add(new_tenant)
    db.session.flush()

    # Yangi oshxona uchun standart Sozlamalar (Setting) yaratish
    new_setting = Setting(
        tenant_id=new_tenant.id,
        card_number="8600 0000 0000 0000",
        card_name=name,
        work_time_start="09:00",
        work_time_end="22:00"
    )
    db.session.add(new_setting)

    # Agar menyuni klonlash tanlangan bo'lsa, 1-oshxonadan ko'chiramiz
    if clone_menu:
        try:
            base_cats = Category.query.filter_by(tenant_id=1).all()
            for cat in base_cats:
                new_cat = Category(
                    tenant_id=new_tenant.id,
                    name=cat.name,
                    name_ru=cat.name_ru,
                    name_en=cat.name_en
                )
                db.session.add(new_cat)
                db.session.flush()

                cat_menus = Menu.query.filter_by(category_id=cat.id, tenant_id=1).all()
                for m in cat_menus:
                    new_menu = Menu(
                        tenant_id=new_tenant.id,
                        category_id=new_cat.id,
                        name=m.name,
                        name_ru=m.name_ru,
                        name_en=m.name_en,
                        description=m.description,
                        description_ru=m.description_ru,
                        description_en=m.description_en,
                        price=m.price,
                        old_price=m.old_price,
                        calories=m.calories,
                        image_url=m.image_url
                    )
                    db.session.add(new_menu)
        except Exception as ce:
            print(f"[Clone menu error]: {ce}")

    db.session.commit()

    # Telegram bot komandalari va WebApp tugmasini avtomatik sozlash
    try:
        raw_url = os.getenv("RENDER_EXTERNAL_URL", "") or os.getenv("WEB_APP_URL", "")
        base_url = raw_url.strip().rstrip('/') if raw_url else ""
        if base_url and not base_url.startswith('http'):
            base_url = f"https://{base_url}"
        web_app_url = f"{base_url}/webapp?tenant={slug}" if base_url else f"https://your-app.onrender.com/webapp?tenant={slug}"

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/setMyCommands",
            json={
                "commands": [
                    {"command": "start", "description": "Botni qayta ishga tushirish"},
                    {"command": "menu", "description": "Menyuni ochish"},
                    {"command": "help", "description": "Yordam va bog'lanish"}
                ]
            },
            timeout=8
        )
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/setChatMenuButton",
            json={
                "menu_button": {
                    "type": "web_app",
                    "text": "🍔 Menyu",
                    "web_app": {"url": web_app_url}
                }
            },
            timeout=8
        )
        requests.post(f"https://api.telegram.org/bot{bot_token}/deleteWebhook", timeout=8)
    except Exception as e:
        print(f"[Auto bot setup error]: {e}")

    return jsonify({'success': True, 'tenant_id': new_tenant.id, 'slug': new_tenant.slug})


@app.route('/api/superadmin/tenants/<int:tenant_id>/toggle', methods=['POST'])
@super_admin_required
def api_superadmin_tenants_toggle(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'success': False, 'error': 'Oshxona topilmadi'}), 404
    tenant.is_active = not bool(tenant.is_active)
    db.session.commit()
    return jsonify({'success': True, 'is_active': tenant.is_active})


@app.route('/api/superadmin/tenants/<int:tenant_id>/impersonate', methods=['POST'])
@super_admin_required
def api_superadmin_tenants_impersonate(tenant_id):
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'success': False, 'error': 'Oshxona topilmadi'}), 404
    session['user_type'] = 'tenant_admin'
    session['tenant_id'] = tenant.id
    session['tenant_slug'] = tenant.slug
    session['tenant_name'] = tenant.name
    session['username'] = tenant.admin_username
    session['is_impersonating'] = True
    return jsonify({'success': True, 'redirect': '/admin'})


@app.route('/api/superadmin/tenants/<int:tenant_id>/delete', methods=['POST'])
@super_admin_required
def api_superadmin_tenants_delete(tenant_id):
    if tenant_id == 1:
        return jsonify({'success': False, 'error': "Asosiy boshlang'ich oshxonani o'chirib bo'lmaydi!"}), 400
    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return jsonify({'success': False, 'error': 'Oshxona topilmadi'}), 404

    Menu.query.filter_by(tenant_id=tenant_id).delete()
    Category.query.filter_by(tenant_id=tenant_id).delete()
    Order.query.filter_by(tenant_id=tenant_id).delete()
    OrderItem.query.filter_by(tenant_id=tenant_id).delete()
    Promotion.query.filter_by(tenant_id=tenant_id).delete()
    PromoCode.query.filter_by(tenant_id=tenant_id).delete()
    Setting.query.filter_by(tenant_id=tenant_id).delete()
    User.query.filter_by(tenant_id=tenant_id).delete()
    Cart.query.filter_by(tenant_id=tenant_id).delete()
    db.session.delete(tenant)
    db.session.commit()
    return jsonify({'success': True})


# --- Bitepoint Modern POS & Admin Panel Routes ---
@app.route('/')
def index_redirect():
    if session.get('user_type') == 'super_admin':
        return redirect('/superadmin')
    elif session.get('user_type') == 'tenant_admin':
        return redirect('/admin')
    return redirect('/login')

@app.route('/admin')
@app.route('/admin/')
@login_required
def bitepoint_admin():
    if session.get('user_type') == 'super_admin' and not session.get('is_impersonating'):
        return redirect('/superadmin')
    return render_template('admin/bitepoint_admin.html')

@app.route('/api/admin/me')
@login_required
def api_admin_me():
    tenant = get_current_tenant()
    return jsonify({
        'success': True,
        'tenant': {
            'id': tenant.id if tenant else 1,
            'name': tenant.name if tenant else "Cafe Express",
            'slug': tenant.slug if tenant else "express",
            'bot_username': tenant.bot_username if tenant else "@CafeExpressBot",
            'admin_username': tenant.admin_username if tenant else "admin"
        },
        'is_impersonating': bool(session.get('is_impersonating', False))
    })


# --- REST API for Bitepoint Admin ---

@app.route('/api/admin/orders')
@login_required
def api_admin_orders():
    t_id = get_current_tenant_id()
    orders = Order.query.filter_by(tenant_id=t_id).order_by(Order.id.desc()).all()
    result = []
    for o in orders:
        created_dt = o.created_at
        if created_dt:
            tashkent_dt = created_dt + timedelta(hours=5)
            date_str = tashkent_dt.strftime("%d-%b, %Y")
            time_str = tashkent_dt.strftime("%H:%M")
        else:
            date_str = "Noma'lum"
            time_str = "--:--"

        items_list = []
        for it in o.items:
            items_list.append({
                'id': it.id,
                'menu_item_id': it.menu_item_id,
                'name': it.name,
                'price': it.price or 0,
                'quantity': it.quantity or 1
            })

        user_phone = o.user.phone if o.user else "—"
        user_lat = o.user.latitude if o.user else None
        user_lon = o.user.longitude if o.user else None

        result.append({
            'id': o.id,
            'user_id': o.user_id,
            'user_phone': user_phone,
            'latitude': user_lat,
            'longitude': user_lon,
            'status': o.status or 'Kutilmoqda',
            'payment_method': o.payment_method or 'Naqd',
            'receipt_image': o.receipt_image,
            'total_amount': o.total_amount or 0,
            'address': o.address or 'N/A',
            'promocode': getattr(o, 'promocode', None) or '',
            'created_date': date_str,
            'created_time': time_str,
            'items': items_list
        })
    return jsonify({'success': True, 'orders': result})


@app.route('/api/admin/orders/<int:order_id>/status', methods=['POST'])
@login_required
def api_admin_order_status(order_id):
    t_id = get_current_tenant_id()
    order = Order.query.filter_by(id=order_id, tenant_id=t_id).first()
    if not order:
        return jsonify({'success': False, 'error': 'Buyurtma topilmadi'}), 404
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    new_status = data.get('status')
    if not new_status:
        return jsonify({'success': False, 'error': 'Status kiritilmadi'}), 400

    order.status = new_status
    db.session.commit()

    send_telegram_order_status_update(order.user_id, order.id, new_status, order.payment_method, order.total_amount, tenant_id=order.tenant_id or t_id)
    return jsonify({'success': True, 'status': new_status})


@app.route('/api/admin/orders/<int:order_id>/delete', methods=['POST'])
@login_required
def api_admin_order_delete(order_id):
    t_id = get_current_tenant_id()
    order = Order.query.filter_by(id=order_id, tenant_id=t_id).first()
    if not order:
        return jsonify({'success': False, 'error': 'Buyurtma topilmadi'}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/menu')
@login_required
def api_admin_menu():
    t_id = get_current_tenant_id()
    menus = Menu.query.filter_by(tenant_id=t_id).all()
    return jsonify({
        'success': True,
        'menu': [{
            'id': m.id,
            'category_id': m.category_id,
            'name': m.name,
            'name_ru': getattr(m, 'name_ru', None) or m.name,
            'name_en': getattr(m, 'name_en', None) or m.name,
            'description': m.description or '',
            'description_ru': getattr(m, 'description_ru', None) or m.description or '',
            'description_en': getattr(m, 'description_en', None) or m.description or '',
            'price': m.price or 0,
            'old_price': m.old_price or 0,
            'calories': getattr(m, 'calories', 0) or 0,
            'image_url': m.image_url or ''
        } for m in menus]
    })


@app.route('/api/admin/menu/create', methods=['POST'])
@login_required
def api_admin_menu_create():
    t_id = get_current_tenant_id()
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Taom nomi kiritilmadi'}), 400

    # Avtomatik tarjima (agar kiritilmagan bo'lsa)
    name_ru = data.get('name_ru', '').strip()
    if not name_ru or name_ru == name:
        name_ru = translate_text(name, 'ru') or name

    name_en = data.get('name_en', '').strip()
    if not name_en or name_en == name:
        name_en = translate_text(name, 'en') or name

    description = data.get('description', '').strip()
    description_ru = data.get('description_ru', '').strip()
    if description and (not description_ru or description_ru == description):
        description_ru = translate_text(description, 'ru') or description

    description_en = data.get('description_en', '').strip()
    if description and (not description_en or description_en == description):
        description_en = translate_text(description, 'en') or description

    try:
        calories = int(data.get('calories', 0) or 0)
    except:
        calories = 0

    menu = Menu(
        tenant_id=t_id,
        name=name,
        name_ru=name_ru,
        name_en=name_en,
        category_id=int(data.get('category_id', 1)),
        price=int(data.get('price', 0)),
        old_price=int(data.get('old_price', 0)),
        calories=calories,
        description=description,
        description_ru=description_ru,
        description_en=description_en,
        image_url=data.get('image_url', '')
    )
    db.session.add(menu)
    db.session.commit()

    # Yangi taom haqida oshxona mijozlariga reklama xabarini yuborish
    try:
        desc_clean = (menu.description or '').strip()
        desc_line = f"📝 {desc_clean}\n" if desc_clean else ""
        formatted_price = f"{menu.price:,}".replace(',', ' ')
        cal_line = f"🔥 Kaloriya: <b>{menu.calories} kkal</b>\n" if menu.calories > 0 else ""
        ad_text = (
            f"✨ <b>BIZDA YANGI TAOM!</b>\n\n"
            f"🍽️ <b>{menu.name}</b>\n"
            f"💰 Narxi: <b>{formatted_price} so'm</b>\n"
            f"{cal_line}"
            f"{desc_line}\n"
            f"😋 Hoziroq Mini App ga kiring va tatib ko'ring! 🚀"
        )
        photo_target = menu.image_url if menu.image_url else None
        broadcast_to_users(ad_text, photo_target, tenant_id=t_id)
    except Exception as be:
        print(f"[Broadcast menu error]: {be}")

    return jsonify({'success': True, 'id': menu.id})


@app.route('/api/admin/menu/<int:item_id>/update', methods=['POST'])
@login_required
def api_admin_menu_update(item_id):
    t_id = get_current_tenant_id()
    menu = Menu.query.filter_by(id=item_id, tenant_id=t_id).first()
    if not menu:
        return jsonify({'success': False, 'error': 'Taom topilmadi'}), 404
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    
    if 'name' in data:
        menu.name = data.get('name', menu.name).strip()
        if not data.get('name_ru'):
            menu.name_ru = translate_text(menu.name, 'ru') or menu.name
        if not data.get('name_en'):
            menu.name_en = translate_text(menu.name, 'en') or menu.name

    if 'name_ru' in data and data.get('name_ru', '').strip():
        menu.name_ru = data.get('name_ru').strip()
    if 'name_en' in data and data.get('name_en', '').strip():
        menu.name_en = data.get('name_en').strip()

    if 'category_id' in data:
        menu.category_id = int(data.get('category_id', menu.category_id))
    if 'price' in data:
        menu.price = int(data.get('price', menu.price))
    if 'old_price' in data:
        menu.old_price = int(data.get('old_price', menu.old_price or 0))
    if 'calories' in data:
        try:
            menu.calories = int(data.get('calories', 0) or 0)
        except:
            pass

    if 'description' in data:
        menu.description = data.get('description', menu.description)
        if not data.get('description_ru'):
            menu.description_ru = translate_text(menu.description, 'ru') or menu.description
        if not data.get('description_en'):
            menu.description_en = translate_text(menu.description, 'en') or menu.description

    if 'description_ru' in data and data.get('description_ru', '').strip():
        menu.description_ru = data.get('description_ru').strip()
    if 'description_en' in data and data.get('description_en', '').strip():
        menu.description_en = data.get('description_en').strip()

    if 'image_url' in data:
        menu.image_url = data.get('image_url', menu.image_url)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/menu/<int:item_id>/delete', methods=['POST'])
@login_required
def api_admin_menu_delete(item_id):
    t_id = get_current_tenant_id()
    menu = Menu.query.filter_by(id=item_id, tenant_id=t_id).first()
    if not menu:
        return jsonify({'success': False, 'error': 'Taom topilmadi'}), 404
    db.session.delete(menu)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/categories')
@login_required
def api_admin_categories():
    t_id = get_current_tenant_id()
    categories = Category.query.filter_by(tenant_id=t_id).all()
    return jsonify({
        'success': True,
        'categories': [{
            'id': c.id, 
            'name': c.name,
            'name_ru': getattr(c, 'name_ru', None) or c.name,
            'name_en': getattr(c, 'name_en', None) or c.name
        } for c in categories]
    })


@app.route('/api/admin/category/create', methods=['POST'])
@login_required
def api_admin_category_create():
    t_id = get_current_tenant_id()
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Kategoriya nomi kiritilmadi'}), 400

    name_ru = data.get('name_ru', '').strip()
    if not name_ru or name_ru == name:
        name_ru = translate_text(name, 'ru') or name

    name_en = data.get('name_en', '').strip()
    if not name_en or name_en == name:
        name_en = translate_text(name, 'en') or name

    cat = Category(
        tenant_id=t_id,
        name=name,
        name_ru=name_ru,
        name_en=name_en
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify({'success': True, 'id': cat.id})


@app.route('/api/admin/category/<int:cat_id>/update', methods=['POST'])
@login_required
def api_admin_category_update(cat_id):
    t_id = get_current_tenant_id()
    cat = Category.query.filter_by(id=cat_id, tenant_id=t_id).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Kategoriya topilmadi'}), 404
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    name = data.get('name', '').strip()
    if name:
        cat.name = name
        if not data.get('name_ru'):
            cat.name_ru = translate_text(name, 'ru') or name
        if not data.get('name_en'):
            cat.name_en = translate_text(name, 'en') or name

    if 'name_ru' in data and data.get('name_ru', '').strip():
        cat.name_ru = data.get('name_ru').strip()
    if 'name_en' in data and data.get('name_en', '').strip():
        cat.name_en = data.get('name_en').strip()

    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/category/<int:cat_id>/delete', methods=['POST'])
@login_required
def api_admin_category_delete(cat_id):
    t_id = get_current_tenant_id()
    cat = Category.query.filter_by(id=cat_id, tenant_id=t_id).first()
    if not cat:
        return jsonify({'success': False, 'error': 'Kategoriya topilmadi'}), 404
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/promotions')
@login_required
def api_admin_promotions():
    t_id = get_current_tenant_id()
    promos = Promotion.query.filter_by(tenant_id=t_id).order_by(Promotion.id.desc()).all()
    return jsonify({
        'success': True,
        'promotions': [{
            'id': p.id,
            'title': p.title,
            'title_ru': getattr(p, 'title_ru', None) or p.title,
            'title_en': getattr(p, 'title_en', None) or p.title,
            'description': p.description or '',
            'description_ru': getattr(p, 'description_ru', None) or p.description or '',
            'description_en': getattr(p, 'description_en', None) or p.description or '',
            'discount_percent': p.discount_percent or 0,
            'end_date': p.end_date or '',
            'category_id': p.category_id,
            'menu_item_id': p.menu_item_id,
            'image_url': p.image_url or '',
            'is_active': bool(p.is_active)
        } for p in promos]
    })


@app.route('/api/admin/promotion/create', methods=['POST'])
@login_required
def api_admin_promotion_create():
    t_id = get_current_tenant_id()
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'error': 'Aksiya sarlavhasi kiritilmadi'}), 400
    promo = Promotion(
        tenant_id=t_id,
        title=title,
        title_ru=data.get('title_ru', '').strip() or title,
        title_en=data.get('title_en', '').strip() or title,
        description=data.get('description', ''),
        description_ru=data.get('description_ru', '').strip() or data.get('description', ''),
        description_en=data.get('description_en', '').strip() or data.get('description', ''),
        discount_percent=int(data.get('discount_percent', 0)),
        end_date=data.get('end_date', ''),
        is_active=True
    )
    db.session.add(promo)
    db.session.commit()
    return jsonify({'success': True, 'id': promo.id})


@app.route('/api/admin/promotion/<int:promo_id>/toggle', methods=['POST'])
@login_required
def api_admin_promotion_toggle(promo_id):
    t_id = get_current_tenant_id()
    promo = Promotion.query.filter_by(id=promo_id, tenant_id=t_id).first()
    if not promo:
        return jsonify({'success': False, 'error': 'Aksiya topilmadi'}), 404
    promo.is_active = not bool(promo.is_active)
    db.session.commit()
    return jsonify({'success': True, 'is_active': promo.is_active})


@app.route('/api/admin/promotion/<int:promo_id>/delete', methods=['POST'])
@login_required
def api_admin_promotion_delete(promo_id):
    t_id = get_current_tenant_id()
    promo = Promotion.query.filter_by(id=promo_id, tenant_id=t_id).first()
    if not promo:
        return jsonify({'success': False, 'error': 'Aksiya topilmadi'}), 404
    db.session.delete(promo)
    db.session.commit()
    return jsonify({'success': True})


# --- Promocode API Endpoints ---

@app.route('/api/admin/promocodes')
@login_required
def api_admin_promocodes():
    t_id = get_current_tenant_id()
    promos = PromoCode.query.filter_by(tenant_id=t_id).order_by(PromoCode.id.desc()).all()
    return jsonify({
        'success': True,
        'promocodes': [{
            'id': p.id,
            'code': p.code,
            'discount_percent': p.discount_percent,
            'end_date': getattr(p, 'end_date', '') or '',
            'min_order_amount': getattr(p, 'min_order_amount', 0) or 0,
            'max_order_amount': getattr(p, 'max_order_amount', 0) or 0,
            'is_active': bool(p.is_active),
            'times_used': p.times_used or 0,
            'created_at': p.created_at.strftime('%Y-%m-%d %H:%M') if p.created_at else ''
        } for p in promos]
    })


@app.route('/api/admin/promocode/create', methods=['POST'])
@login_required
def api_admin_promocode_create():
    t_id = get_current_tenant_id()
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    code = (data.get('code') or '').strip().upper()
    try:
        discount_percent = int(data.get('discount_percent', 0))
    except:
        discount_percent = 0

    end_date = (data.get('end_date') or '').strip() or None
    try:
        min_order_amount = int(data.get('min_order_amount', 0))
    except:
        min_order_amount = 0

    try:
        max_order_amount = int(data.get('max_order_amount', 0))
    except:
        max_order_amount = 0

    if not code:
        return jsonify({'success': False, 'error': 'Promokod kiritilishi shart!'}), 400
    if discount_percent <= 0 or discount_percent > 100:
        return jsonify({'success': False, 'error': 'Chegirma foizi 1% dan 100% gacha bo\'lishi kerak!'}), 400

    existing = PromoCode.query.filter_by(code=code, tenant_id=t_id).first()
    if existing:
        return jsonify({'success': False, 'error': f"'{code}' nomli promokod allaqachon mavjud!"}), 400

    promo = PromoCode(
        tenant_id=t_id,
        code=code,
        discount_percent=discount_percent,
        end_date=end_date,
        min_order_amount=min_order_amount,
        max_order_amount=max_order_amount,
        is_active=True
    )
    db.session.add(promo)
    db.session.commit()

    # Yangi promokod haqida oshxona mijozlariga reklama xabarini yuborish
    try:
        cond_lines = []
        if min_order_amount > 0 and max_order_amount > 0:
            cond_lines.append(f"💳 Buyurtma summasi: <b>{min_order_amount:,} - {max_order_amount:,} so'm</b> oralig'ida".replace(',', ' '))
        elif min_order_amount > 0:
            cond_lines.append(f"💳 Minimal buyurtma: <b>{min_order_amount:,} so'm</b>".replace(',', ' '))
        elif max_order_amount > 0:
            cond_lines.append(f"💳 Maksimal buyurtma: <b>{max_order_amount:,} so'm</b> gacha".replace(',', ' '))

        if end_date:
            cond_lines.append(f"⏳ Amal qilish muddati: <b>{end_date}</b> gacha")

        cond_text = ("\n".join(cond_lines) + "\n") if cond_lines else ""

        ad_text = (
            f"🎟️ <b>YANGI CHEGIRMA PROMO-KODI!</b>\n\n"
            f"💥 Bizda ajoyib chegirma boshlandi!\n"
            f"🔑 Promokod: <code>{code}</code>\n"
            f"🏷️ Chegirma: <b>-{discount_percent}%</b>\n"
            f"{cond_text}\n"
            f"🍔 Hoziroq Mini App ga kiring va buyurtma bering! 🚀"
        )
        broadcast_to_users(ad_text, tenant_id=t_id)
    except Exception as be:
        print(f"[Broadcast promo error]: {be}")

    return jsonify({
        'success': True,
        'id': promo.id,
        'promocode': {
            'id': promo.id,
            'code': promo.code,
            'discount_percent': promo.discount_percent,
            'end_date': promo.end_date or '',
            'min_order_amount': promo.min_order_amount or 0,
            'max_order_amount': promo.max_order_amount or 0
        }
    })


@app.route('/api/admin/promocode/<int:promo_id>/toggle', methods=['POST'])
@login_required
def api_admin_promocode_toggle(promo_id):
    t_id = get_current_tenant_id()
    promo = PromoCode.query.filter_by(id=promo_id, tenant_id=t_id).first()
    if not promo:
        return jsonify({'success': False, 'error': 'Promokod topilmadi'}), 404
    promo.is_active = not bool(promo.is_active)
    db.session.commit()
    return jsonify({'success': True, 'is_active': promo.is_active})


@app.route('/api/admin/promocode/<int:promo_id>/delete', methods=['POST'])
@login_required
def api_admin_promocode_delete(promo_id):
    t_id = get_current_tenant_id()
    promo = PromoCode.query.filter_by(id=promo_id, tenant_id=t_id).first()
    if not promo:
        return jsonify({'success': False, 'error': 'Promokod topilmadi'}), 404
    db.session.delete(promo)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/validate_promocode', methods=['POST'])
def api_validate_promocode():
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    code = (data.get('code') or '').strip().upper()
    try:
        order_amount = int(data.get('order_amount', 0))
    except:
        order_amount = 0

    if not code:
        return jsonify({'success': False, 'error': 'Promokod kiritilmadi'}), 400

    tenant_param = data.get('tenant', '').strip()
    tenant_obj = None
    if tenant_param:
        tenant_obj = Tenant.query.filter((Tenant.slug == tenant_param.lower()) | (Tenant.id == tenant_param)).first()
    if not tenant_obj:
        tenant_obj = Tenant.query.first()
    t_id = tenant_obj.id if tenant_obj else 1

    promo = PromoCode.query.filter_by(code=code, tenant_id=t_id).first()
    if not promo:
        return jsonify({'success': False, 'error': 'Bunday promokod mavjud emas!'})

    is_valid, error_msg = check_promocode_validity(promo, order_amount)
    if not is_valid:
        return jsonify({'success': False, 'error': error_msg})

    return jsonify({
        'success': True,
        'code': promo.code,
        'discount_percent': promo.discount_percent,
        'end_date': getattr(promo, 'end_date', '') or '',
        'min_order_amount': getattr(promo, 'min_order_amount', 0) or 0,
        'max_order_amount': getattr(promo, 'max_order_amount', 0) or 0
    })


@app.route('/api/admin/settings')
@login_required
def api_admin_get_settings():
    t_id = get_current_tenant_id()
    setting = Setting.query.filter_by(tenant_id=t_id).first()
    if not setting:
        t_obj = Tenant.query.get(t_id)
        default_name = t_obj.name if t_obj else "Admin"
        setting = Setting(tenant_id=t_id, card_number="8600 0000 0000 0000", card_name=default_name, work_time_start="09:00", work_time_end="22:00")
        db.session.add(setting)
        db.session.commit()
    return jsonify({
        'success': True,
        'settings': {
            'card_number': setting.card_number or '',
            'card_name': setting.card_name or '',
            'work_time_start': getattr(setting, 'work_time_start', '09:00') or '09:00',
            'work_time_end': getattr(setting, 'work_time_end', '22:00') or '22:00'
        }
    })


@app.route('/api/admin/settings/update', methods=['POST'])
@login_required
def api_admin_update_settings():
    t_id = get_current_tenant_id()
    data = request.get_json(force=True, silent=True) or request.form.to_dict() or {}
    setting = Setting.query.filter_by(tenant_id=t_id).first()
    if not setting:
        setting = Setting(tenant_id=t_id)
        db.session.add(setting)
    setting.card_number = data.get('card_number', setting.card_number)
    setting.card_name = data.get('card_name', setting.card_name)
    setting.work_time_start = data.get('work_time_start', getattr(setting, 'work_time_start', '09:00'))
    setting.work_time_end = data.get('work_time_end', getattr(setting, 'work_time_end', '22:00'))
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/admin/stats')
@login_required
def api_admin_stats():
    t_id = get_current_tenant_id()
    orders = Order.query.filter_by(tenant_id=t_id).all()
    today_orders_count = 0
    today_revenue = 0
    cash_revenue = 0
    card_revenue = 0
    pending_orders = 0
    dish_sales = {}

    tz = timezone(timedelta(hours=5))
    now = datetime.now(tz)
    today_date_str = now.strftime("%Y-%m-%d")

    for o in orders:
        if o.status == 'Kutilmoqda':
            pending_orders += 1

        order_dt = o.created_at
        is_today = False
        if order_dt:
            tashkent_dt = order_dt + timedelta(hours=5)
            if tashkent_dt.strftime("%Y-%m-%d") == today_date_str:
                is_today = True

        if is_today and o.status != 'Bekor qilindi':
            today_orders_count += 1
            amount = o.total_amount or 0
            today_revenue += amount
            if o.payment_method == 'Karta':
                card_revenue += amount
            else:
                cash_revenue += amount

        if o.status != 'Bekor qilindi':
            for item in o.items:
                dish_sales[item.name] = dish_sales.get(item.name, 0) + (item.quantity or 1)

    avg_order = int(today_revenue / today_orders_count) if today_orders_count > 0 else 0
    top_dishes = sorted([{'name': k, 'qty': v} for k, v in dish_sales.items()], key=lambda x: x['qty'], reverse=True)[:5]

    return jsonify({
        'success': True,
        'stats': {
            'today_revenue': today_revenue,
            'today_orders': today_orders_count,
            'avg_order': avg_order,
            'pending_orders': pending_orders,
            'cash_revenue': cash_revenue,
            'card_revenue': card_revenue,
            'top_dishes': top_dishes
        }
    })


@app.route('/api/admin/upload_image', methods=['POST'])
def api_admin_upload_image():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'Rasm tanlanmagan'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Fayl nomi bo\'sh'}), 400

    filename = str(uuid.uuid4())[:8] + "_" + secure_filename(file.filename or 'food.jpg')
    menu_dir = os.path.join(app.root_path, 'static', 'uploads', 'menu')
    os.makedirs(menu_dir, exist_ok=True)
    file_path = os.path.join(menu_dir, filename)
    file.save(file_path)
    return jsonify({'success': True, 'image_url': f'/static/uploads/menu/{filename}'})


# --- Flask-Admin Fallback Panel ---
class ThemedModelView(ModelView):
    extra_css = ['/static/admin_theme.css']

class MenuAdminView(ThemedModelView):
    column_list = ('id', 'category', 'name', 'description', 'price', 'old_price', 'image_url')
    form_columns = ['category', 'name', 'description', 'price', 'old_price', 'image_url']
    can_create = True
    can_edit = True
    can_delete = True

def _receipt_link(view, context, model, name):
    if not model.receipt_image:
        return Markup('<span style="color:gray">Chek yo\'q</span>')
    return Markup(f'<a href="/static/uploads/receipts/{model.receipt_image}" target="_blank" style="color:blue">📎 Chekni ko\'rish</a>')

def _order_items_display(view, context, model, name):
    if not model.items:
        return ''
    lines = [f"{oi.name} x{oi.quantity} = {oi.price * oi.quantity:,} so'm" for oi in model.items]
    return Markup('<br>'.join(lines))

def _user_phone(view, context, model, name):
    if model.user:
        return model.user.phone or '—'
    return '—'

def _format_datetime(view, context, model, name):
    if not model.created_at:
        return ''
    tashkent_time = model.created_at + timedelta(hours=5)
    return tashkent_time.strftime("%Y-%m-%d %H:%M:%S")

def _display_order_id(view, context, model, name):
    display_no = model.daily_id or model.id
    return Markup(f"<b>#{display_no}</b>")

class OrderAdminView(ModelView):
    list_template = 'admin/order_list.html'
    extra_css = ['/static/admin_theme.css']
    column_default_sort = ('id', 'desc')
    column_list = ('daily_id', 'user_phone', 'order_items_text', 'total_amount', 'payment_method', 'address', 'status', 'receipt_image', 'created_at')
    column_labels = {
        'daily_id': 'Buyurtma №',
        'user_phone': 'Telefon',
        'order_items_text': 'Buyurtma tarkibi',
        'total_amount': 'Jami (so\'m)',
        'payment_method': 'To\'lov',
        'address': 'Manzil',
        'status': 'Holat',
        'receipt_image': 'Chek',
        'created_at': 'Vaqt'
    }
    column_formatters = {
        'daily_id': _display_order_id,
        'receipt_image': _receipt_link,
        'order_items_text': _order_items_display,
        'user_phone': _user_phone,
        'created_at': _format_datetime,
    }
    form_choices = {
        'status': [
            ('Kutilmoqda', '⏳ Kutilmoqda'),
            ('Tayyorlanmoqda', '🔥 Tayyorlanmoqda'),
            ('Tasdiqlandi', '✅ Tasdiqlandi'),
            ('Tugatildi', '🏁 Tugatildi'),
            ('Bekor qilindi', '❌ Bekor qilindi')
        ]
    }
    form_columns = ['status']
    can_create = False
    can_delete = True

    def get_query(self):
        return super(OrderAdminView, self).get_query().options(
            joinedload(Order.user),
            subqueryload(Order.items)
        )

    def after_model_change(self, form, model, is_created):
        """Admin statusni o'zgartirganda mijozga xabar yuborish (Mutloq xavfsiz va tezkor)"""
        try:
            user_id = model.user_id
            order_id = model.id
            order_no = model.daily_id or model.id
            status = model.status
            payment = model.payment_method or "Naqd"
            total = model.total_amount or 0

            # Agar order.user_id bot foydalanuvchisi emas bo'lsa (0 bo'lsa), uning telefon raqami bo'yicha DB dan user_id ni izlaymiz
            if (not user_id or str(user_id) == '0') and model.user and model.user.phone:
                found_user = User.query.filter(User.phone == model.user.phone, User.user_id != 0).first()
                if found_user:
                    user_id = found_user.user_id
                    try:
                        model.user_id = found_user.user_id
                        db.session.commit()
                    except Exception as e:
                        print(f"[DB user update error]: {e}")

            if status == 'Tasdiqlandi':
                if payment == 'Karta':
                    msg = (
                        f"✅ #{order_no}-raqamli buyurtmangiz TASDIQLANDI!\n\n"
                        f"💳 To'lovingiz qabul qilindi!\n"
                        f"💰 Jami: {total:,} so'm\n\n"
                        f"🚚 Buyurtmangiz tez orada yetkazib beriladi. Rahmat! 🙏"
                    )
                else:
                    msg = (
                        f"✅ #{order_no}-raqamli buyurtmangiz TASDIQLANDI!\n\n"
                        f"💵 To'lov turi: Naqd\n"
                        f"💰 Jami: {total:,} so'm\n\n"
                        f"🚚 Buyurtmangiz tez orada yetkazib beriladi. Rahmat! 🙏"
                    )
            elif status == 'Bekor qilindi':
                msg = (
                    f"❌ #{order_no}-raqamli buyurtmangiz BEKOR QILINDI!\n\n"
                    f"Qo'shimcha ma'lumot uchun biz bilan bog'laning."
                )
            else:
                return  # Kutilmoqda holatida xabar yuborma

            target_uid = user_id
            def send_status_msg():
                token = os.getenv("BOT_TOKEN")
                if token and target_uid and str(target_uid) not in ('0', '', 'None'):
                    try:
                        resp = requests.post(
                            f"https://api.telegram.org/bot{token}/sendMessage",
                            json={"chat_id": int(target_uid), "text": msg},
                            timeout=10
                        )
                        print(f"[Admin status notify] Status '{status}' -> user {target_uid}: HTTP {resp.status_code} - {resp.text}", flush=True)
                    except Exception as e:
                        print("[Admin status notify error]:", e, flush=True)
                else:
                    print(f"[Admin status notify warning]: Telegram xabar yuborilmadi. target_uid={target_uid}", flush=True)

            threading.Thread(target=send_status_msg, daemon=True).start()
        except Exception as err:
            print("[after_model_change error]:", err, flush=True)

class OrderItemAdminView(ModelView):
    column_list = ('id', 'order_id', 'name', 'price', 'quantity')
    column_labels = {
        'order_id': 'Buyurtma №',
        'name': 'Mahsulot',
        'price': 'Narx',
        'quantity': 'Miqdor'
    }
    can_create = False
    can_edit = False
    can_delete = False


# --- Admin Panel Ko'rinishlari (Views) ---
class ThemedModelView(ModelView):
    extra_css = ['/static/admin_theme.css']

class SettingAdminView(ThemedModelView):
    column_list = ('card_number', 'card_name', 'work_time_start', 'work_time_end', 'order_reset_hours')
    column_labels = {
        'card_number': 'Karta Raqami',
        'card_name': 'Karta Egasi',
        'work_time_start': 'Ish Boshlanishi (hh:mm)',
        'work_time_end': 'Ish Tugashi (hh:mm)',
        'order_reset_hours': 'Buyurtma Raqami Reset Intervali (Soat)'
    }
    form_columns = ['card_number', 'card_name', 'work_time_start', 'work_time_end', 'order_reset_hours']
    form_widget_args = {
        'order_reset_hours': {
            'help': 'Masalan: 24 (har 24 soatda buyurtma #1 dan boshlanadi), 12 (har 12 soatda 1-dan boshlanadi), 0 (reset o\'chiriladi). Eski buyurtmalar tarixdan yo\'qolmaydi!'
        }
    }
    can_create = False
    can_delete = False

    def after_model_change(self, form, model, is_created):
        try:
            # Sozlamalar o'zgarganda daily_id larni qayta hisoblash
            orders_list = Order.query.order_by(Order.id.asc()).all()
            rh = model.order_reset_hours or 24
            prev_dt = None
            curr_daily_id = 0
            for o in orders_list:
                dt_val = None
                if o.created_at:
                    if isinstance(o.created_at, str):
                        try:
                            dt_val = datetime.strptime(o.created_at.split('.')[0], "%Y-%m-%d %H:%M:%S")
                        except:
                            dt_val = None
                    elif isinstance(o.created_at, datetime):
                        dt_val = o.created_at

                if rh == 0:
                    curr_daily_id += 1
                    o.daily_id = curr_daily_id
                else:
                    if prev_dt is None or dt_val is None:
                        curr_daily_id = 1
                    else:
                        diff_h = (dt_val - prev_dt).total_seconds() / 3600.0
                        if diff_h >= rh:
                            curr_daily_id = 1
                        else:
                            curr_daily_id += 1
                    o.daily_id = curr_daily_id

                if dt_val:
                    prev_dt = dt_val

            db.session.commit()
        except Exception as e:
            print(f"[Setting update recalculate error]: {e}")

class PromotionAdminView(ThemedModelView):
    column_list = ('id', 'title', 'description', 'discount_percent', 'end_date', 'category', 'menu_item', 'is_active', 'created_at')
    form_columns = ['title', 'description', 'discount_percent', 'end_date', 'category', 'menu_item', 'image_url', 'is_active']
    can_create = True
    can_edit = True
    can_delete = True

flask_admin = Admin(app, name='☕ Cafe Express DB', url='/flask-admin', endpoint='flask_admin')
flask_admin.add_view(OrderAdminView(Order, db.session, name="📦 Buyurtmalar"))
flask_admin.add_view(MenuAdminView(Menu, db.session, name="🍔 Menyu (Taomlar)"))
flask_admin.add_view(PromotionAdminView(Promotion, db.session, name="🏷️ Chegirmalar"))
flask_admin.add_view(ThemedModelView(Category, db.session, name="📁 Kategoriyalar"))
flask_admin.add_view(SettingAdminView(Setting, db.session, name="⚙️ Sozlamalar"))
flask_admin.add_view(ThemedModelView(User, db.session, name="👤 Mijozlar"))

if __name__ == '__main__':
    print("Cafe Express Admin panel ishga tushdi: http://127.0.0.1:5000/admin")
    app.run(host='127.0.0.1', port=5000)

