import os
import requests
import json
import threading
import uuid
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload, subqueryload
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, AdminIndexView, expose
from flask import redirect, url_for
from markupsafe import Markup

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

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __repr__(self):
        return f"<User {self.phone}>"

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    menus = db.relationship('Menu', backref='category', lazy=True)

    def __repr__(self):
        return self.name

class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    price = db.Column(db.Integer)
    old_price = db.Column(db.Integer, default=0) # Eski narx (ustidan chizilgan)
    image_url = db.Column(db.String(500))

    def __repr__(self):
        return self.name

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    quantity = db.Column(db.Integer)
    user = db.relationship('User', backref='cart_items')
    item = db.relationship('Menu', backref='cart_entries')

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
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

class OrderItem(db.Model):
    """Buyurtma tarkibidagi har bir mahsulot"""
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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
    daily_id = db.Column(db.Integer, default=1) # Har kunlik/soatlik 1, 2, 3... tartib raqam
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    status = db.Column(db.String(50), default="Kutilmoqda")
    payment_method = db.Column(db.String(50))
    receipt_image = db.Column(db.String(500))
    total_amount = db.Column(db.Integer)
    address = db.Column(db.String(500))
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
            
        # Menu migration
        menu_cols = [col['name'] for col in inspector.get_columns('menu')]
        if 'old_price' not in menu_cols:
            db.session.execute(text("ALTER TABLE menu ADD COLUMN old_price INTEGER DEFAULT 0"))

        # Promotions migration
        promo_cols = [col['name'] for col in inspector.get_columns('promotions')]
        if 'end_date' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN end_date VARCHAR(100)"))
        if 'category_id' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN category_id INTEGER"))
        if 'menu_item_id' not in promo_cols:
            db.session.execute(text("ALTER TABLE promotions ADD COLUMN menu_item_id INTEGER"))

        db.session.commit()

        # Existing buyurtmalarga kunlik daily_id larni to'g'ri ketma-ketlikda (#1, #2, #3...) qayta berish (Auto-repair)
        orders_all = Order.query.order_by(Order.id.asc()).all()
        date_groups = {}
        for o in orders_all:
            if o.created_at:
                try:
                    if isinstance(o.created_at, str):
                        dt_obj = datetime.strptime(o.created_at.split('.')[0], "%Y-%m-%d %H:%M:%S")
                    else:
                        dt_obj = o.created_at
                    day_str = (dt_obj + timedelta(hours=5)).strftime("%Y-%m-%d")
                except:
                    day_str = "2026-08-01"
            else:
                day_str = "2026-08-01"
            
            date_groups[day_str] = date_groups.get(day_str, 0) + 1
            o.daily_id = date_groups[day_str]
        db.session.commit()
    except Exception as e:
        print(f"[Auto-migration error]: {e}")

# --- WebApp API ---
@app.route('/webapp')
def webapp():
    return render_template('webapp.html')

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
    categories = Category.query.all()
    menus = Menu.query.all()
    setting = Setting.query.first()
    promotions = Promotion.query.filter_by(is_active=True).all()
    
    return jsonify({
        'categories': [{'id': c.id, 'name': c.name} for c in categories],
        'menu': [{
            'id': m.id, 
            'category_id': m.category_id, 
            'name': m.name, 
            'description': m.description, 
            'price': m.price, 
            'old_price': getattr(m, 'old_price', 0) or 0,
            'image_url': m.image_url
        } for m in menus],
        'promotions': [{
            'id': p.id,
            'title': p.title,
            'description': p.description,
            'discount_percent': p.discount_percent,
            'end_date': p.end_date,
            'category_id': p.category_id,
            'menu_item_id': p.menu_item_id,
            'image_url': p.image_url
        } for p in promotions],
        'settings': {
            'card_number': setting.card_number if setting else "8600 0000 0000 0000",
            'card_name': setting.card_name if setting else "Ism Familiya"
        }
    })

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """1-qadam: Buyurtmani tezda saqlash va javob qaytarish (UI qotib qolmaydi)"""
    try:
        # Ish vaqtini tekshirish
        setting = Setting.query.first()
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

        user_id = str(data.get('user_id', '')).strip()
        phone = str(data.get('phone', '')).strip()
        address = str(data.get('address', '')).strip()
        payment_method = str(data.get('payment_method', 'Naqd'))
        items_raw = data.get('items', '[]')
        latitude = data.get('latitude', 0)
        longitude = data.get('longitude', 0)

        # Agar user_id kelmagan yoki '0' bo'lsa, DB dan ushbu telefon raqamli foydalanuvchini izlaymiz
        if (not user_id or user_id == '0') and phone:
            found_u = User.query.filter(User.phone == phone, User.user_id != 0).first()
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
        active_promotions = Promotion.query.filter_by(is_active=True).all()

        for item in items:
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
                user_obj = User.query.get(parsed_uid)
                if not user_obj:
                    user_obj = User(user_id=parsed_uid, phone=phone, latitude=lat_val, longitude=lon_val)
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
        setting = Setting.query.first()
        reset_hours = getattr(setting, 'order_reset_hours', 24)
        if reset_hours is None:
            reset_hours = 24

        tz = timezone(timedelta(hours=5)) # Tashkent time UTC+5
        now_tz = datetime.now(tz)

        if reset_hours == 0:
            total_orders = Order.query.count()
            next_daily_id = total_orders + 1
        elif reset_hours == 24:
            # Toshkent vaqti bilan bugungi kun boshlangandan buyon tushgan buyurtmalar soni + 1
            today_start_tz = now_tz.replace(hour=0, minute=0, second=0, microsecond=0)
            today_start_utc = today_start_tz.astimezone(timezone.utc).replace(tzinfo=None)
            orders_today = Order.query.filter(Order.created_at >= today_start_utc).count()
            next_daily_id = orders_today + 1
        else:
            cutoff_tz = now_tz - timedelta(hours=reset_hours)
            cutoff_utc = cutoff_tz.astimezone(timezone.utc).replace(tzinfo=None)
            recent_orders = Order.query.filter(Order.created_at >= cutoff_utc).count()
            next_daily_id = recent_orders + 1

        # Buyurtmani DB ga saqlash
        new_order = Order(
            daily_id=next_daily_id,
            user_id=int(user_id) if str(user_id).isdigit() else 0,
            status="Kutilmoqda",
            payment_method=payment_method,
            receipt_image=receipt_filename,
            total_amount=total_amount,
            address=address
        )
        db.session.add(new_order)
        db.session.flush()

        for oi in order_items_data:
            db.session.add(OrderItem(
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
        order_text = (
            f"🆕 YANGI BUYURTMA #{order_no}!\n\n"
            f"👤 Mijoz: {phone}\n"
            f"📍 Manzil: {address}\n"
            f"💳 To'lov: {payment_method}\n\n"
            f"🛒 Tarkib:\n{order_text_items}"
            f"💰 Jami: {total_amount:,} so'm\n"
        )

        def notify_all():
            bot_token = os.getenv("BOT_TOKEN")
            admin_id = os.getenv("ADMIN_ID")
            if not bot_token:
                print("[Notify warning]: BOT_TOKEN sozlanmagan!")
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
    items_text = ""
    for oi in order.items:
        items_text += f"• {oi.name} x{oi.quantity} = {oi.price * oi.quantity:,} so'm\n"

    def send_receipt_to_admin():
        bot_token = os.getenv("BOT_TOKEN")
        admin_id = os.getenv("ADMIN_ID")
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


# --- Model Ko'rinishlari (Views) sozlamalari ---
class ThemedModelView(ModelView):
    extra_css = ['/static/admin_theme.css']

class MenuAdminView(ThemedModelView):
    column_list = ('id', 'category', 'name', 'description', 'price', 'old_price', 'image_url')
    column_labels = {
        'id': '№',
        'category': 'Kategoriya',
        'name': 'Nomi',
        'description': 'Tavsif',
        'price': 'Sotuv Narxi (so\'m)',
        'old_price': 'Eski Narxi (Ustidan chiziladi)',
        'image_url': 'Rasm URL'
    }
    form_columns = ['category', 'name', 'description', 'price', 'old_price', 'image_url']
    can_create = True
    can_edit = True
    can_delete = True

    def get_query(self):
        return super(MenuAdminView, self).get_query().options(joinedload(Menu.category))

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
    from datetime import timedelta
    # Add 5 hours for Tashkent time (UTC+5)
    tashkent_time = model.created_at + timedelta(hours=5)
    return tashkent_time.strftime("%Y-%m-%d %H:%M:%S")

def _display_order_id(view, context, model, name):
    display_no = model.daily_id or model.id
    return Markup(f"<b>#{display_no}</b>")

class OrderAdminView(ModelView):
    # Admin panelda ko'rinadigan ustunlar
    list_template = 'admin/order_list.html'
    extra_css = ['/static/admin_theme.css']
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
    column_extra_row_actions = []
    form_choices = {
        'status': [
            ('Kutilmoqda', '⏳ Kutilmoqda'),
            ('Tasdiqlandi', '✅ Tasdiqlandi'),
            ('Bekor qilindi', '❌ Bekor qilindi')
        ]
    }
    form_columns = ['status']
    can_create = False
    can_delete = False

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

class PromotionAdminView(ThemedModelView):
    column_list = ('id', 'title', 'description', 'discount_percent', 'end_date', 'category', 'menu_item', 'is_active', 'created_at')
    column_labels = {
        'id': '№',
        'title': 'Chegirma Nomi',
        'description': 'Tavsif / Shartlar',
        'discount_percent': 'Chegirma (%)',
        'end_date': 'Tugash Vaqti (yyyy-mm-dd hh:mm)',
        'category': 'Kategoriya (Ixtiyoriy)',
        'menu_item': 'Taom (Ixtiyoriy)',
        'image_url': 'Rasm URL',
        'is_active': 'Faollik',
        'created_at': 'Vaqt'
    }
    form_columns = ['title', 'description', 'discount_percent', 'end_date', 'category', 'menu_item', 'image_url', 'is_active']
    can_create = True
    can_edit = True
    can_delete = True

class MyHomeView(AdminIndexView):
    @expose('/')
    def index(self):
        return redirect('/admin/order/')
    
    def is_visible(self):
        return False

admin = Admin(app, name='☕ Cafe Express Admin', index_view=MyHomeView(url='/admin'))
admin.add_view(OrderAdminView(Order, db.session, name="📦 Buyurtmalar"))
admin.add_view(MenuAdminView(Menu, db.session, name="🍔 Menyu (Taomlar)"))
admin.add_view(PromotionAdminView(Promotion, db.session, name="🏷️ Chegirmalar"))
admin.add_view(ThemedModelView(Category, db.session, name="📁 Kategoriyalar"))
admin.add_view(SettingAdminView(Setting, db.session, name="⚙️ Sozlamalar"))
admin.add_view(ThemedModelView(User, db.session, name="👤 Mijozlar"))

if __name__ == '__main__':
    print("Admin panel ishga tushdi: http://127.0.0.1:5000/admin")
    app.run(host='127.0.0.1', port=5000)
