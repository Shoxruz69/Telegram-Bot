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
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from markupsafe import Markup

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-restaurant-key'
app.config['FLASK_ADMIN_SWATCH'] = 'flatly'

# Baza fayli joylashgan manzil
db_path = os.path.join(os.path.dirname(__file__), 'database', 'restaurant.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

    def __repr__(self):
        return f"Karta: {self.card_number} ({self.card_name})"

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
        return f"Buyurtma #{self.id} - {self.status}"

# --- Jadvallarni yaratish ---
with app.app_context():
    db.create_all()
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('settings')]
        if 'work_time_start' not in columns:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN work_time_start VARCHAR(10) DEFAULT '09:00'"))
        if 'work_time_end' not in columns:
            db.session.execute(text("ALTER TABLE settings ADD COLUMN work_time_end VARCHAR(10) DEFAULT '22:00'"))
        db.session.commit()
    except Exception as e:
        print("Auto-migration xatosi:", e)

# --- WebApp API ---
@app.route('/webapp')
def webapp():
    return render_template('webapp.html')

@app.route('/ping')
def ping():
    return "OK", 200

@app.route('/api/data')
def api_data():
    categories = Category.query.all()
    menus = Menu.query.all()
    setting = Setting.query.first()
    
    return jsonify({
        'categories': [{'id': c.id, 'name': c.name} for c in categories],
        'menu': [{
            'id': m.id, 
            'category_id': m.category_id, 
            'name': m.name, 
            'description': m.description, 
            'price': m.price, 
            'image_url': m.image_url
        } for m in menus],
        'settings': {
            'card_number': setting.card_number if setting else "8600 0000 0000 0000",
            'card_name': setting.card_name if setting else "Ism Familiya"
        }
    })

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    """1-qadam: Buyurtmani tezda saqlash va javob qaytarish (UI qotib qolmaydi)"""
    # Ish vaqtini tekshirish
    setting = Setting.query.first()
    if setting and getattr(setting, 'work_time_start', None) and getattr(setting, 'work_time_end', None):
        tz = timezone(timedelta(hours=5))
        now = datetime.now(tz)
        current_time_str = now.strftime("%H:%M")
        start = setting.work_time_start
        end = setting.work_time_end
        if start <= end:
            if not (start <= current_time_str <= end):
                return jsonify({'success': False, 'error': f"Ish vaqti tugadi! Bizning ish vaqtimiz {start} dan {end} gacha."})
        else:
            if not (current_time_str >= start or current_time_str <= end):
                return jsonify({'success': False, 'error': f"Ish vaqti tugadi! Bizning ish vaqtimiz {start} dan {end} gacha."})

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            data = request.form.to_dict()
    except:
        data = request.form.to_dict()

    user_id = str(data.get('user_id', ''))
    phone = str(data.get('phone', ''))
    address = str(data.get('address', ''))
    payment_method = str(data.get('payment_method', 'Naqd'))
    items_raw = data.get('items', '[]')
    latitude = data.get('latitude', 0)
    longitude = data.get('longitude', 0)

    if not user_id or not phone:
        return jsonify({'success': False, 'error': "Telefon raqam yoki user_id yo'q!"})

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

    for item in items:
        menu_item = Menu.query.get(int(item['id']))
        if menu_item:
            qty = int(item['qty'])
            price = menu_item.price
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
        user_obj = User.query.get(int(user_id))
        if not user_obj:
            user_obj = User(user_id=int(user_id), phone=phone, latitude=lat_val, longitude=lon_val)
            db.session.add(user_obj)
        else:
            user_obj.phone = phone
            user_obj.latitude = lat_val
            user_obj.longitude = lon_val
    except:
        pass

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
            receipts_dir = os.path.join(app.root_path, 'static', 'uploads', 'receipts')
            os.makedirs(receipts_dir, exist_ok=True)
            with open(os.path.join(receipts_dir, receipt_filename), 'wb') as f:
                f.write(file_data)
        except Exception as e:
            print(f"[Base64 decode error]: {e}")

    # Buyurtmani DB ga saqlash
    new_order = Order(
        user_id=int(user_id),
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

    # Admin va mijozga FONDA xabar yuborish (UI ni kuttiradigan narsa yo'q)
    order_text = (
        f"🆕 YANGI BUYURTMA #{order_id}!\n\n"
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
            return
        # Admin xabari
        if admin_id and admin_id not in ("YOUR_ADMIN_ID_HERE", "", None):
            try:
                # Agar chek bo'lsa, rasmli xabar yuboramiz
                if receipt_filename:
                    with open(os.path.join(receipts_dir, receipt_filename), 'rb') as photo:
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
                if lat_val and lon_val and lat_val != 0.0:
                    requests.post(
                        f"https://api.telegram.org/bot{bot_token}/sendLocation",
                        json={'chat_id': admin_id, 'latitude': lat_val, 'longitude': lon_val},
                        timeout=12
                    )
            except Exception as e:
                print(f"[Admin notify error]: {e}")
        # Mijoz xabari
        try:
            user_msg = (
                f"✅ Buyurtmangiz #{order_id} qabul qilindi!\n"
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
    return jsonify({'success': True, 'order_id': order_id})


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

uploads_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads')

class MenuAdminView(ModelView):
    extra_css = ['/static/admin_theme.css']
    column_list = ('id', 'category', 'name', 'description', 'price', 'image_url')
    column_labels = {
        'id': '№',
        'category': 'Kategoriya',
        'name': 'Nomi',
        'description': 'Tavsif',
        'price': 'Narx (so\'m)',
        'image_url': 'Rasm URL'
    }
    form_columns = ['category', 'name', 'description', 'price', 'image_url']
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
    from datetime import timedelta
    # Add 5 hours for Tashkent time (UTC+5)
    tashkent_time = model.created_at + timedelta(hours=5)
    return tashkent_time.strftime("%Y-%m-%d %H:%M:%S")

class OrderAdminView(ModelView):
    # Admin panelda ko'rinadigan ustunlar
    list_template = 'admin/order_list.html'
    extra_css = ['/static/admin_theme.css']
    column_list = ('id', 'user_phone', 'order_items_text', 'total_amount', 'payment_method', 'address', 'status', 'receipt_image', 'created_at')
    column_labels = {
        'id': '№',
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
    # Faqat status va address tahrirlash mumkin
    form_columns = ['status']
    can_create = False
    can_delete = False

    def after_model_change(self, form, model, is_created):
        """Admin statusni o'zgartirganda mijozga xabar yuborish"""
        if model.status == 'Tasdiqlandi':
            if model.payment_method == 'Karta':
                msg = (
                    f"✅ #{model.id}-raqamli buyurtmangiz TASDIQLANDI!\n\n"
                    f"💳 To'lovingiz qabul qilindi!\n"
                    f"💰 Jami: {model.total_amount:,} so'm\n\n"
                    f"🚚 Buyurtmangiz tez orada yetkazib beriladi. Rahmat! 🙏"
                )
            else:
                msg = (
                    f"✅ #{model.id}-raqamli buyurtmangiz TASDIQLANDI!\n\n"
                    f"💵 To'lov turi: Naqd\n"
                    f"💰 Jami: {model.total_amount:,} so'm\n\n"
                    f"🚚 Buyurtmangiz tez orada yetkazib beriladi. Rahmat! 🙏"
                )
        elif model.status == 'Bekor qilindi':
            msg = (
                f"❌ #{model.id}-raqamli buyurtmangiz BEKOR QILINDI!\n\n"
                f"Qo'shimcha ma'lumot uchun biz bilan bog'laning."
            )
        else:
            return  # Kutilmoqda holatida xabar yuborma
            
        token = os.getenv("BOT_TOKEN")
        if token and model.user_id:
            try:
                resp = requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": model.user_id, "text": msg},
                    timeout=10
                )
                print(f"[Admin] Status '{model.status}' -> user {model.user_id}: {resp.status_code}")
            except Exception as e:
                print("Error sending telegram message:", e)

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

admin = Admin(app, name='☕ Cafe Express Admin')
admin.add_view(OrderAdminView(Order, db.session, name="📦 Buyurtmalar"))
admin.add_view(MenuAdminView(Menu, db.session, name="🍔 Menyu (Taomlar)"))
admin.add_view(ThemedModelView(Category, db.session, name="📁 Kategoriyalar"))
admin.add_view(ThemedModelView(Setting, db.session, name="⚙️ Sozlamalar"))
admin.add_view(ThemedModelView(User, db.session, name="👤 Mijozlar"))

if __name__ == '__main__':
    print("Admin panel ishga tushdi: http://127.0.0.1:5000/admin")
    app.run(host='127.0.0.1', port=5000)
