/**
 * BITEPOINT POS & RESTAURANT ADMIN SYSTEM - JAVASCRIPT
 * Multi-Language: Uzbek (uz), Russian (ru), English (en)
 */

// I18N DICTIONARY
const i18n = {
  uz: {
    // Navigation
    orders: "Buyurtmalar",
    menu: "Menyu",
    categories: "Kategoriyalar",
    discounts: "Chegirmalar",
    accounting: "Hisobot",
    settings: "Sozlamalar",
    client_app: "Mijoz WebApp",
    admin_role: "Admin / Menejer",
    
    // Status Filters & Header
    all: "Barchasi",
    on_process: "Jarayonda",
    completed: "Bajarildi",
    cancelled: "Bekor qilindi",
    search_placeholder: "Qidirish (ism, tel, buyurtma #)...",
    new_btn: "Yangi",
    add_dish: "Yangi Taom",
    add_category: "Yangi Kategoriya",
    add_discount: "Yangi Aksiya",

    // Order Card
    order: "Buyurtma",
    dine_in: "Zalda",
    takeaway: "Olib ketish",
    delivery: "Yetkazib berish",
    table: "Stol",
    dishes_col: "Taomlar",
    qty_col: "Soni",
    price_col: "Narxi",
    total_lbl: "Jami:",
    see_details: "Batafsil",
    pay_bills: "To'lov / Tasdiqlash",
    complete_order: "Tugatish ✓",
    view_btn: "Ko'rish",
    receipt_attached: "Chek mavjud",
    cash: "Naqd",
    card: "Karta",
    more_items: "ta ko'proq...",
    no_orders_found: "Hozircha buyurtmalar yo'q",
    no_orders_sub: "Ushbu filtr bo'yicha hech qanday buyurtma topilmadi.",

    // Status Texts
    status_ready: "✓ Tasdiqlandi",
    status_ready_sub: "Tayyor / Yetkazilmoqda",
    status_cooking: "🔥 Oshxonada",
    status_cooking_sub: "Tayyorlanmoqda",
    status_pending: "⏳ Kutilmoqda",
    status_pending_sub: "Tasdiqlash kerak",
    status_cancelled: "✕ Bekor qilindi",
    status_cancelled_sub: "Rad etildi",

    // Payment / Details Modal
    modal_payment_title: "To'lov va Buyurtma Tafsilotlari",
    modal_items_subtotal: "Mahsulotlar summasi:",
    modal_delivery_fee: "Yetkazish / Xizmat:",
    modal_grand_total: "Jami To'lov:",
    modal_cancel_order: "❌ Buyurtmani Bekor Qilish",
    modal_received_amount: "Mijozdan qabul qilingan summa:",
    modal_change: "Qaytim (Сдача):",
    modal_need_more: "Yana",
    modal_need_more_suffix: "kerak",
    modal_pay_now: "⚡ Tasdiqlash (Mijozga xabar yuborish)",
    modal_card_receipt_alert: "💳 Karta To'lovi Cheki Yuklangan",
    modal_view_receipt: "Chekni Ko'rish",
    view_map: "🗺️ Xaritada ko'rish",
    address_lbl: "Manzil:",
    not_specified: "Ko'rsatilmagan",

    // Menu Management
    menu_management_title: "Menyu Boshqaruvi",
    all_categories: "Barchasi",
    edit_btn: "✏️ Tahrirlash",
    delete_btn: "🗑️",
    add_dish_modal_title: "Yangi Taom Qo'shish",
    edit_dish_modal_title: "Taomni Tahrirlash",
    dish_name_lbl: "Taom Nomi",
    dish_name_placeholder: "Masalan: Double Cheeseburger",
    dish_category_lbl: "Kategoriya",
    dish_price_lbl: "Sotuv Narxi (so'm)",
    dish_old_price_lbl: "Eski Narxi (Aksiya uchun)",
    dish_desc_lbl: "Tavsif / Tarkibi",
    dish_desc_placeholder: "Taom haqida qisqacha ma'lumot...",
    dish_image_lbl: "Rasm URL yoki Fayldan yuklash",
    save_btn: "💾 Saqlash",

    // Categories
    categories_title: "Kategoriyalar Boshqaruvi",
    cat_dishes_count: "ta taom mavjud",
    add_cat_modal_title: "Yangi Kategoriya Qo'shish",
    edit_cat_modal_title: "Kategoriyani Tahrirlash",
    cat_name_lbl: "Kategoriya Nomi",
    cat_name_placeholder: "Masalan: Milliy Taomlar",

    // Discounts & Promotions
    discounts_title: "Aksiyalar & Chegirmalar",
    active_promo: "Faol Aksiya",
    inactive_promo: "Nofaol",
    end_date_lbl: "Tugash vaqti:",
    turn_on: "Yoqish",
    turn_off: "O'chirish",
    add_promo_modal_title: "Yangi Aksiya / Chegirma",
    promo_title_lbl: "Aksiya Sarlavhasi",
    promo_discount_lbl: "Chegirma Foizi (%)",
    promo_end_date_lbl: "Tugash Sanasi va Vaqti",
    promo_desc_lbl: "Aksiya Shartlari / Tavsifi",
    promocodes: "Promokodlar",
    add_promocode: "Yangi Promokod",
    promocode_lbl: "Promokod Kodi",
    promocode_discount_lbl: "Chegirma Foizi (%)",
    times_used_suffix: "marta ishlatildi",
    promocode_saved: "Promokod muvaffaqiyatli saqlandi!",
    promocode_deleted: "Promokod o'chirildi!",
    no_promocodes_found: "Hozircha promokodlar yo'q",
    promo_expiry_lbl: "Muddati:",
    promo_range_lbl: "Buyurtma summasi:",
    promo_all_orders: "Barcha buyurtmalarga",
    promo_unlimited: "Cheksiz",

    // Accounting & Stats
    accounting_title: "Kassa & Hisobot",
    today_revenue: "Bugungi Savdo",
    today_orders: "Buyurtmalar Soni",
    avg_order: "O'rtacha Chek",
    pending_orders: "Kutilayotgan",
    payment_split_title: "💳 To'lov Turlari Taqsimoti",
    cash_split_lbl: "💵 Naqd to'lov:",
    card_split_lbl: "💳 Karta orqali:",
    top_dishes_title: "🏆 Eng Ko'p Sotilgan Taomlar",
    sold_qty_suffix: "ta sotildi",
    no_sales_yet: "Hozircha sotuvlar yo'q",

    // Settings
    settings_title: "Sozlamalar",
    settings_box_title: "⚙️ Tizim va To'lov Sozlamalari",
    card_number_lbl: "Karta Raqami (Mijozlar to'lashi uchun)",
    card_name_lbl: "Karta Egasi Ism-Familiyasi",
    work_start_lbl: "Ish Vaqti Boshi",
    work_end_lbl: "Ish Vaqti Tugashi",
    save_settings_btn: "💾 Sozlamalarni Saqlash",

    // Toasts
    order_status_updated: "Buyurtma statusi o'zgartirildi!",
    order_cancelled_confirm: "Buyurtmani bekor qilishga ishonchingiz komilmi?",
    dish_saved: "Taom muvaffaqiyatli saqlandi!",
    dish_deleted: "Taom o'chirildi!",
    category_saved: "Kategoriya muvaffaqiyatli saqlandi!",
    category_deleted: "Kategoriya o'chirildi!",
    promo_saved: "Aksiya saqlandi!",
    settings_saved: "Sozlamalar muvaffaqiyatli saqlandi!",
    img_uploading: "Rasm yuklanmoqda...",
    img_uploaded: "Rasm muvaffaqiyatli yuklandi!",
    new_order_toast: "🔔 Yangi buyurtma qabul qilindi!"
  },

  ru: {
    // Navigation
    orders: "Заказы",
    menu: "Меню",
    categories: "Категории",
    discounts: "Акции",
    accounting: "Бухгалтерия",
    settings: "Настройки",
    client_app: "Клиентское WebApp",
    admin_role: "Админ / Менеджер",

    // Status Filters & Header
    all: "Все",
    on_process: "В процессе",
    completed: "Завершенные",
    cancelled: "Отмененные",
    search_placeholder: "Поиск (имя, телефон, заказ #)...",
    new_btn: "Новый",
    add_dish: "Добавить блюдо",
    add_category: "Добавить категорию",
    add_discount: "Добавить акцию",

    // Order Card
    order: "Заказ",
    dine_in: "В зале",
    takeaway: "С собой",
    delivery: "Доставка",
    table: "Стол",
    dishes_col: "Блюда",
    qty_col: "Кол-во",
    price_col: "Сумма",
    total_lbl: "Итого:",
    see_details: "Детали",
    pay_bills: "Оплата / Принять",
    complete_order: "Завершить ✓",
    view_btn: "Просмотр",
    receipt_attached: "Чек прикреплен",
    cash: "Наличные",
    card: "Картой",
    more_items: "еще...",
    no_orders_found: "Заказов пока нет",
    no_orders_sub: "По данному фильтру заказов не найдено.",

    // Status Texts
    status_ready: "✓ Подтвержден",
    status_ready_sub: "Готов / В пути",
    status_cooking: "🔥 На кухне",
    status_cooking_sub: "Готовится",
    status_pending: "⏳ Ожидает",
    status_pending_sub: "Требует подтверждения",
    status_cancelled: "✕ Отменен",
    status_cancelled_sub: "Отклонен",

    // Payment / Details Modal
    modal_payment_title: "Детали заказа и оплата",
    modal_items_subtotal: "Сумма товаров:",
    modal_delivery_fee: "Доставка / Сервис:",
    modal_grand_total: "Итого к оплате:",
    modal_cancel_order: "❌ Отменить заказ",
    modal_received_amount: "Принятая сумма от клиента:",
    modal_change: "Сдача:",
    modal_need_more: "Не хватает еще",
    modal_need_more_suffix: "",
    modal_pay_now: "⚡ Подтвердить (Уведомить клиента)",
    modal_card_receipt_alert: "💳 Чек оплаты картой загружен",
    modal_view_receipt: "Посмотреть чек",
    view_map: "🗺️ На карте",
    address_lbl: "Адрес:",
    not_specified: "Не указан",

    // Menu Management
    menu_management_title: "Управление меню",
    all_categories: "Все",
    edit_btn: "✏️ Изменить",
    delete_btn: "🗑️",
    add_dish_modal_title: "Добавить новое блюдо",
    edit_dish_modal_title: "Редактировать блюдо",
    dish_name_lbl: "Название блюда",
    dish_name_placeholder: "Например: Двойной чизбургер",
    dish_category_lbl: "Категория",
    dish_price_lbl: "Цена продажи (сум)",
    dish_old_price_lbl: "Старая цена (для акции)",
    dish_desc_lbl: "Описание / Состав",
    dish_desc_placeholder: "Краткая информация о блюде...",
    dish_image_lbl: "Ссылка на фото или загрузка",
    save_btn: "💾 Сохранить",

    // Categories
    categories_title: "Управление категориями",
    cat_dishes_count: "блюд доступно",
    add_cat_modal_title: "Добавить категорию",
    edit_cat_modal_title: "Редактировать категорию",
    cat_name_lbl: "Название категории",
    cat_name_placeholder: "Например: Национальные блюда",

    // Discounts & Promotions
    discounts_title: "Акции и скидки",
    active_promo: "Активна",
    inactive_promo: "Неактивна",
    end_date_lbl: "Дата окончания:",
    turn_on: "Включить",
    turn_off: "Отключить",
    add_promo_modal_title: "Новая акция / скидка",
    promo_title_lbl: "Заголовок акции",
    promo_discount_lbl: "Процент скидки (%)",
    promo_end_date_lbl: "Дата и время окончания",
    promo_desc_lbl: "Условия акции / Описание",
    promocodes: "Промокоды",
    add_promocode: "Новый промокод",
    promocode_lbl: "Код промокода",
    promocode_discount_lbl: "Процент скидки (%)",
    times_used_suffix: "раз использован",
    promocode_saved: "Промокод успешно сохранен!",
    promocode_deleted: "Промокод удален!",
    no_promocodes_found: "Пока нет промокодов",
    promo_expiry_lbl: "Срок действия:",
    promo_range_lbl: "Сумма заказа:",
    promo_all_orders: "На все заказы",
    promo_unlimited: "Бессрочно",

    // Accounting & Stats
    accounting_title: "Касса и отчеты",
    today_revenue: "Выручка за сегодня",
    today_orders: "Количество заказов",
    avg_order: "Средний чек",
    pending_orders: "В ожидании",
    payment_split_title: "💳 Распределение способов оплаты",
    cash_split_lbl: "💵 Наличные:",
    card_split_lbl: "💳 Безналичные:",
    top_dishes_title: "🏆 Топ популярных блюд",
    sold_qty_suffix: "шт продано",
    no_sales_yet: "Продаж пока нет",

    // Settings
    settings_title: "Настройки",
    settings_box_title: "⚙️ Настройки системы и реквизиты",
    card_number_lbl: "Номер карты для оплаты",
    card_name_lbl: "Имя владельца карты",
    work_start_lbl: "Время открытия",
    work_end_lbl: "Время закрытия",
    save_settings_btn: "💾 Сохранить настройки",

    // Toasts
    order_status_updated: "Статус заказа обновлен!",
    order_cancelled_confirm: "Вы уверены, что хотите отменить этот заказ?",
    dish_saved: "Блюдо успешно сохранено!",
    dish_deleted: "Блюдо удалено!",
    category_saved: "Категория успешно сохранена!",
    category_deleted: "Категория удалена!",
    promo_saved: "Акция сохранена!",
    settings_saved: "Настройки успешно сохранены!",
    img_uploading: "Изображение загружается...",
    img_uploaded: "Изображение успешно загружено!",
    new_order_toast: "🔔 Принят новый заказ!"
  },

  en: {
    // Navigation
    orders: "Orders",
    menu: "Menu",
    categories: "Categories",
    discounts: "Discounts",
    accounting: "Accounting",
    settings: "Settings",
    client_app: "Customer WebApp",
    admin_role: "Admin / Manager",

    // Status Filters & Header
    all: "All",
    on_process: "On Process",
    completed: "Completed",
    cancelled: "Cancelled",
    search_placeholder: "Search a name, order, or etc",
    new_btn: "New",
    add_dish: "Add Dish",
    add_category: "Add Category",
    add_discount: "Add Discount",

    // Order Card
    order: "Order",
    dine_in: "Dine In",
    takeaway: "Takeaway",
    delivery: "Delivery",
    table: "Table",
    dishes_col: "Items",
    qty_col: "Qty",
    price_col: "Price",
    total_lbl: "Total:",
    see_details: "See Details",
    pay_bills: "Pay Bills",
    complete_order: "Complete ✓",
    view_btn: "View",
    receipt_attached: "Receipt attached",
    cash: "Cash",
    card: "Card",
    more_items: "more...",
    no_orders_found: "No orders yet",
    no_orders_sub: "No orders found matching this filter.",

    // Status Texts
    status_ready: "✓ Ready",
    status_ready_sub: "Ready to serve",
    status_cooking: "🔥 In Kitchen",
    status_cooking_sub: "Cooking Now",
    status_pending: "⏳ In Progress",
    status_pending_sub: "Requires confirmation",
    status_cancelled: "✕ Cancelled",
    status_cancelled_sub: "Rejected",

    // Payment / Details Modal
    modal_payment_title: "Payment & Order Details",
    modal_items_subtotal: "Items Total:",
    modal_delivery_fee: "Delivery / Service:",
    modal_grand_total: "Grand Total:",
    modal_cancel_order: "❌ Cancel Order",
    modal_received_amount: "Amount received from customer:",
    modal_change: "Change:",
    modal_need_more: "Still need",
    modal_need_more_suffix: "more",
    modal_pay_now: "⚡ Pay Now (Confirm Order)",
    modal_card_receipt_alert: "💳 Card Payment Receipt Attached",
    modal_view_receipt: "View Receipt",
    view_map: "🗺️ View on Map",
    address_lbl: "Address:",
    not_specified: "Not specified",

    // Menu Management
    menu_management_title: "Menu Management",
    all_categories: "All",
    edit_btn: "✏️ Edit",
    delete_btn: "🗑️",
    add_dish_modal_title: "Add New Dish",
    edit_dish_modal_title: "Edit Dish",
    dish_name_lbl: "Dish Name",
    dish_name_placeholder: "e.g. Double Cheeseburger",
    dish_category_lbl: "Category",
    dish_price_lbl: "Price (UZS)",
    dish_old_price_lbl: "Old Price (for discount)",
    dish_desc_lbl: "Description / Ingredients",
    dish_desc_placeholder: "Brief information about dish...",
    dish_image_lbl: "Image URL or Upload",
    save_btn: "💾 Save",

    // Categories
    categories_title: "Category Management",
    cat_dishes_count: "dishes available",
    add_cat_modal_title: "Add New Category",
    edit_cat_modal_title: "Edit Category",
    cat_name_lbl: "Category Name",
    cat_name_placeholder: "e.g. Fast Food",

    // Discounts & Promotions
    discounts_title: "Discounts & Promotions",
    active_promo: "Active",
    inactive_promo: "Inactive",
    end_date_lbl: "End date:",
    turn_on: "Activate",
    turn_off: "Deactivate",
    add_promo_modal_title: "New Discount / Promo",
    promo_title_lbl: "Promotion Title",
    promo_discount_lbl: "Discount Percentage (%)",
    promo_end_date_lbl: "End Date and Time",
    promo_desc_lbl: "Terms & Conditions",
    promocodes: "Promo Codes",
    add_promocode: "New Promo Code",
    promocode_lbl: "Promo Code",
    promocode_discount_lbl: "Discount Percentage (%)",
    times_used_suffix: "times used",
    promocode_saved: "Promo code saved successfully!",
    promocode_deleted: "Promo code deleted!",
    no_promocodes_found: "No promo codes yet",
    promo_expiry_lbl: "Expires:",
    promo_range_lbl: "Order amount:",
    promo_all_orders: "All orders",
    promo_unlimited: "No limit",

    // Accounting & Stats
    accounting_title: "Accounting & Reports",
    today_revenue: "Today's Revenue",
    today_orders: "Total Orders",
    avg_order: "Average Check",
    pending_orders: "Pending Orders",
    payment_split_title: "💳 Payment Method Split",
    cash_split_lbl: "💵 Cash:",
    card_split_lbl: "💳 Card:",
    top_dishes_title: "🏆 Top Selling Dishes",
    sold_qty_suffix: "sold",
    no_sales_yet: "No sales yet",

    // Settings
    settings_title: "Settings",
    settings_box_title: "⚙️ System & Payment Settings",
    card_number_lbl: "Card Number (for payments)",
    card_name_lbl: "Card Holder Name",
    work_start_lbl: "Opening Time",
    work_end_lbl: "Closing Time",
    save_settings_btn: "💾 Save Settings",

    // Toasts
    order_status_updated: "Order status updated!",
    order_cancelled_confirm: "Are you sure you want to cancel this order?",
    dish_saved: "Dish saved successfully!",
    dish_deleted: "Dish deleted!",
    category_saved: "Category saved successfully!",
    category_deleted: "Category deleted!",
    promo_saved: "Promotion saved!",
    settings_saved: "Settings saved successfully!",
    img_uploading: "Uploading image...",
    img_uploaded: "Image uploaded successfully!",
    new_order_toast: "🔔 New order received!"
  }
};

// Global App State
const state = {
  lang: localStorage.getItem('bitepoint_lang') || 'uz',
  theme: localStorage.getItem('bitepoint_theme') || 'dark',
  currentTab: 'orders',       // 'orders' | 'menu' | 'categories' | 'promotions' | 'accounting' | 'settings'
  promoSubTab: 'promos',      // 'promos' | 'promocodes'
  orderStatusFilter: 'all',    // 'all' | 'process' | 'completed' | 'cancelled'
  searchQuery: '',
  orders: [],
  categories: [],
  menuItems: [],
  promotions: [],
  promocodes: [],
  settings: {},
  stats: {},
  selectedOrder: null,
  calcInput: '',
  audioEnabled: true,
  lastKnownOrderCount: 0,
  pollTimer: null,
  expandedOrders: new Set()
};

// Translation Helper
function t(key) {
  const currentDict = i18n[state.lang] || i18n.uz;
  return currentDict[key] || key;
}

// Multilingual Helper Getters
function getDishName(dish) {
  if (!dish) return '';
  if (state.lang === 'ru' && dish.name_ru) return dish.name_ru;
  if (state.lang === 'en' && dish.name_en) return dish.name_en;
  return dish.name || '';
}

function getDishDesc(dish) {
  if (!dish) return '';
  if (state.lang === 'ru' && dish.description_ru) return dish.description_ru;
  if (state.lang === 'en' && dish.description_en) return dish.description_en;
  return dish.description || '';
}

function getCategoryName(cat) {
  if (!cat) return '';
  if (state.lang === 'ru' && cat.name_ru) return cat.name_ru;
  if (state.lang === 'en' && cat.name_en) return cat.name_en;
  return cat.name || '';
}

function getPromoTitle(promo) {
  if (!promo) return '';
  if (state.lang === 'ru' && promo.title_ru) return promo.title_ru;
  if (state.lang === 'en' && promo.title_en) return promo.title_en;
  return promo.title || '';
}

function getPromoDesc(promo) {
  if (!promo) return '';
  if (state.lang === 'ru' && promo.description_ru) return promo.description_ru;
  if (state.lang === 'en' && promo.description_en) return promo.description_en;
  return promo.description || '';
}

// Theme Handling
function toggleAdminTheme() {
  const newTheme = state.theme === 'dark' ? 'light' : 'dark';
  state.theme = newTheme;
  localStorage.setItem('bitepoint_theme', newTheme);
  applyAdminTheme();
}

function applyAdminTheme() {
  const isLight = state.theme === 'light';
  document.body.classList.toggle('light-theme', isLight);
  const btn = document.getElementById('admin-theme-btn');
  if (btn) {
    btn.textContent = isLight ? '☀️' : '🌙';
  }
}

// Switch Language
function setLanguage(lang) {
  if (!i18n[lang]) lang = 'uz';
  state.lang = lang;
  localStorage.setItem('bitepoint_lang', lang);

  // Update language selector button active states
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });

  applyTranslationsToStaticElements();
  updateCurrentDate();
  switchTab(state.currentTab);
}

// Sound chime using Web Audio API
function playChimeSound() {
  if (!state.audioEnabled) return;
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const now = ctx.currentTime;
    
    // Note 1: E5 (659.25 Hz)
    const osc1 = ctx.createOscillator();
    const gain1 = ctx.createGain();
    osc1.type = 'sine';
    osc1.frequency.setValueAtTime(659.25, now);
    gain1.gain.setValueAtTime(0.3, now);
    gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.5);
    osc1.connect(gain1);
    gain1.connect(ctx.destination);
    osc1.start(now);
    osc1.stop(now + 0.5);

    // Note 2: G#5 (830.61 Hz)
    const osc2 = ctx.createOscillator();
    const gain2 = ctx.createGain();
    osc2.type = 'sine';
    osc2.frequency.setValueAtTime(830.61, now + 0.12);
    gain2.gain.setValueAtTime(0.3, now + 0.12);
    gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.7);
    osc2.connect(gain2);
    gain2.connect(ctx.destination);
    osc2.start(now + 0.12);
    osc2.stop(now + 0.7);

    // Note 3: B5 (987.77 Hz)
    const osc3 = ctx.createOscillator();
    const gain3 = ctx.createGain();
    osc3.type = 'sine';
    osc3.frequency.setValueAtTime(987.77, now + 0.24);
    gain3.gain.setValueAtTime(0.4, now + 0.24);
    gain3.gain.exponentialRampToValueAtTime(0.001, now + 0.9);
    osc3.connect(gain3);
    gain3.connect(ctx.destination);
    osc3.start(now + 0.24);
    osc3.stop(now + 0.9);
  } catch (e) {
    console.log("Audio not allowed yet:", e);
  }
}

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Format Price
function formatPrice(amount) {
  if (!amount && amount !== 0) return "0 " + (state.lang === 'en' ? "UZS" : "so'm");
  const suffix = state.lang === 'en' ? " UZS" : (state.lang === 'ru' ? " сум" : " so'm");
  return amount.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ") + suffix;
}

// Format Date
function updateCurrentDate() {
  const dateEl = document.getElementById('current-date-text');
  if (dateEl) {
    const options = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
    const locale = state.lang === 'uz' ? 'uz-UZ' : (state.lang === 'ru' ? 'ru-RU' : 'en-US');
    const today = new Date();
    dateEl.textContent = today.toLocaleDateString(locale, options);
  }
}

// Apply Translations to Static HTML
function applyTranslationsToStaticElements() {
  // Sidebar items
  const mapText = (selector, text) => {
    const el = document.querySelector(selector);
    if (el) el.textContent = text;
  };

  mapText('#nav-orders-text', t('orders'));
  mapText('#nav-menu-text', t('menu'));
  mapText('#nav-categories-text', t('categories'));
  mapText('#nav-promotions-text', t('discounts'));
  mapText('#nav-accounting-text', t('accounting'));
  mapText('#nav-settings-text', t('settings'));
  mapText('#user-role-text', t('admin_role'));
  mapText('#btn-webapp-text', t('client_app'));

  // Search input placeholder
  const searchInput = document.getElementById('global-search');
  if (searchInput) searchInput.placeholder = t('search_placeholder');

  // Filter Tabs
  mapText('#tab-all-text', t('all'));
  mapText('#tab-process-text', t('on_process'));
  mapText('#tab-completed-text', t('completed'));
  mapText('#tab-cancelled-text', t('cancelled'));

  // Settings tab titles & labels
  mapText('#lbl-setting-box-title', t('settings_box_title'));
  mapText('#lbl-setting-card-number', t('card_number_lbl'));
  mapText('#lbl-setting-card-name', t('card_name_lbl'));
  mapText('#lbl-setting-work-start', t('work_start_lbl'));
  mapText('#lbl-setting-work-end', t('work_end_lbl'));
  mapText('#btn-save-settings-text', t('save_settings_btn'));

  // Stats labels
  mapText('#stat-today-revenue-title', t('today_revenue'));
  mapText('#stat-today-orders-title', t('today_orders'));
  mapText('#stat-avg-order-title', t('avg_order'));
  mapText('#stat-pending-orders-title', t('pending_orders'));
  mapText('#stat-payment-split-title', t('payment_split_title'));
  mapText('#stat-cash-lbl', t('cash_split_lbl'));
  mapText('#stat-card-lbl', t('card_split_lbl'));
  mapText('#stat-top-dishes-title', t('top_dishes_title'));

  // Modal labels
  mapText('#modal-payment-title-text', t('modal_payment_title'));
  mapText('#modal-subtotal-lbl', t('modal_items_subtotal'));
  mapText('#modal-delivery-lbl', t('modal_delivery_fee'));
  mapText('#modal-grandtotal-lbl', t('modal_grand_total'));
  mapText('#modal-numpad-lbl', t('modal_received_amount'));
  mapText('#modal-change-lbl', t('modal_change'));
  mapText('#btn-pay-now-text', t('modal_pay_now'));
  mapText('#btn-cancel-order-text', t('modal_cancel_order'));
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  // Apply theme immediately
  applyAdminTheme();

  // Set active language button
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === state.lang);
  });

  applyTranslationsToStaticElements();
  updateCurrentDate();
  initNavigation();
  initSearchAndFilters();
  initAudioToggle();
  
  // Initial data load
  fetchOrders(true);
  fetchMenuAndCategories();
  fetchSettings();

  // Start real-time polling every 4 seconds
  state.pollTimer = setInterval(() => {
    if (state.currentTab === 'orders') {
      fetchOrders(false);
    }
  }, 4000);
});

// Navigation Handling
function initNavigation() {
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = item.dataset.tab;
      switchTab(tab);
    });
  });
}

function switchTab(tab) {
  state.currentTab = tab;
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  const activeNavItem = document.querySelector(`.nav-item[data-tab="${tab}"]`);
  if (activeNavItem) activeNavItem.classList.add('active');

  // Hide all view panels
  document.querySelectorAll('.view-panel').forEach(p => p.style.display = 'none');
  
  // Show target view panel
  const targetPanel = document.getElementById(`view-${tab}`);
  if (targetPanel) targetPanel.style.display = 'block';

  // Update page header title
  const titleEl = document.getElementById('header-title');
  const filterTabs = document.getElementById('header-filter-tabs');
  const actionBtn = document.getElementById('header-action-btn');

  if (tab === 'orders') {
    titleEl.textContent = t('orders');
    filterTabs.style.display = 'flex';
    actionBtn.style.display = 'none';
    fetchOrders(false);
  } else if (tab === 'menu') {
    titleEl.textContent = t('menu_management_title');
    filterTabs.style.display = 'none';
    actionBtn.style.display = 'flex';
    actionBtn.innerHTML = `<span>➕</span> <span>${t('add_dish')}</span>`;
    actionBtn.onclick = () => openDishModal();
    renderMenuView();
  } else if (tab === 'categories') {
    titleEl.textContent = t('categories_title');
    filterTabs.style.display = 'none';
    actionBtn.style.display = 'flex';
    actionBtn.innerHTML = `<span>➕</span> <span>${t('add_category')}</span>`;
    actionBtn.onclick = () => openCategoryModal();
    renderCategoriesView();
  } else if (tab === 'promotions') {
    titleEl.textContent = t('discounts_title');
    filterTabs.style.display = 'none';
    actionBtn.style.display = 'flex';
    switchPromoSubTab(state.promoSubTab || 'promos');
  } else if (tab === 'accounting') {
    titleEl.textContent = t('accounting_title');
    filterTabs.style.display = 'none';
    actionBtn.style.display = 'none';
    fetchStats();
  } else if (tab === 'settings') {
    titleEl.textContent = t('settings_title');
    filterTabs.style.display = 'none';
    actionBtn.style.display = 'none';
    fetchSettings();
  }
}

// Search and Filter Handling
function initSearchAndFilters() {
  const searchInput = document.getElementById('global-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      state.searchQuery = e.target.value.toLowerCase().trim();
      if (state.currentTab === 'orders') {
        renderOrdersGrid();
      } else if (state.currentTab === 'menu') {
        renderMenuView();
      }
    });
  }

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.orderStatusFilter = btn.dataset.status;
      renderOrdersGrid();
    });
  });
}

// Audio Alert Toggle
function initAudioToggle() {
  const btn = document.getElementById('btn-audio-toggle');
  if (btn) {
    btn.addEventListener('click', () => {
      state.audioEnabled = !state.audioEnabled;
      btn.classList.toggle('active', state.audioEnabled);
      showToast(state.audioEnabled ? "🔔 " + (state.lang === 'ru' ? "Звук включен" : state.lang === 'en' ? "Sound enabled" : "Ovozli bildirishnoma yoqildi") : "🔕 " + (state.lang === 'ru' ? "Звук отключен" : state.lang === 'en' ? "Sound disabled" : "Ovozli bildirishnoma o'chirildi"), "info");
      if (state.audioEnabled) playChimeSound();
    });
  }
}

// ==========================================================================
// ORDERS LOGIC & RENDERING
// ==========================================================================

async function fetchOrders(isFirstLoad = false) {
  try {
    const res = await fetch('/api/admin/orders');
    const data = await res.json();
    if (data.success) {
      const oldOrdersMap = new Map(state.orders.map(o => [o.id, o]));
      const newOrders = data.orders || [];

      // Detect new incoming orders for sound chime and notification
      if (!isFirstLoad && newOrders.length > state.orders.length) {
        const latestNewOrder = newOrders[0];
        if (latestNewOrder && (!oldOrdersMap.has(latestNewOrder.id) || latestNewOrder.status === 'Kutilmoqda')) {
          playChimeSound();
          showToast(`${t('new_order_toast')} #${latestNewOrder.id} (${formatPrice(latestNewOrder.total_amount)})`, 'success');
        }
      }

      state.orders = newOrders;
      updateOrderCounts();
      renderOrdersGrid();
    }
  } catch (err) {
    console.error("Error fetching orders:", err);
  }
}

function updateOrderCounts() {
  const counts = { all: 0, process: 0, completed: 0, cancelled: 0 };
  let pendingCount = 0;

  state.orders.forEach(o => {
    counts.all++;
    const s = o.status;
    if (s === 'Kutilmoqda' || s === 'Tayyorlanmoqda') {
      counts.process++;
      if (s === 'Kutilmoqda') pendingCount++;
    } else if (s === 'Tasdiqlandi' || s === 'Tugatildi') {
      counts.completed++;
    } else if (s === 'Bekor qilindi') {
      counts.cancelled++;
    }
  });

  const countAll = document.getElementById('count-all');
  const countProcess = document.getElementById('count-process');
  const countCompleted = document.getElementById('count-completed');
  const countCancelled = document.getElementById('count-cancelled');
  const navOrdersBadge = document.getElementById('nav-orders-badge');

  if (countAll) countAll.textContent = counts.all;
  if (countProcess) countProcess.textContent = counts.process;
  if (countCompleted) countCompleted.textContent = counts.completed;
  if (countCancelled) countCancelled.textContent = counts.cancelled;

  if (navOrdersBadge) {
    if (pendingCount > 0) {
      navOrdersBadge.textContent = pendingCount;
      navOrdersBadge.style.display = 'inline-block';
    } else {
      navOrdersBadge.style.display = 'none';
    }
  }
}

// Generate letter tag for orders (e.g. A4, B2, TA, DL)
function getOrderBadgeInfo(order, index) {
  if (order.address && (order.address.toLowerCase().includes('olib ketish') || order.address.toLowerCase().includes('takeaway') || order.address.toLowerCase().includes('с собой'))) {
    return { text: 'TA', colorClass: 'amber', subtext: t('takeaway') };
  }
  if (order.address && (order.address.toLowerCase().includes('stol') || order.address.toLowerCase().includes('table') || order.address.toLowerCase().includes('стол'))) {
    const match = order.address.match(/\d+/);
    const num = match ? match[0] : (index + 1);
    return { text: `S${num}`, colorClass: 'teal', subtext: `${t('table')} #${num}` };
  }
  const badges = ['A4', 'B2', 'C1', 'D3', 'E5', 'F2', 'TA', 'DL'];
  const colors = ['teal', 'blue', 'amber', 'dark', 'purple'];
  const badgeText = badges[order.id % badges.length];
  const colorClass = colors[order.id % colors.length];
  return { text: badgeText, colorClass, subtext: t('delivery') };
}

function getStatusPillInfo(status) {
  if (status === 'Tasdiqlandi' || status === 'Tugatildi') {
    return { cls: 'ready', dotText: t('status_ready'), sub: t('status_ready_sub') };
  } else if (status === 'Tayyorlanmoqda') {
    return { cls: 'in-progress', dotText: t('status_cooking'), sub: t('status_cooking_sub') };
  } else if (status === 'Kutilmoqda') {
    return { cls: 'in-progress', dotText: t('status_pending'), sub: t('status_pending_sub') };
  } else if (status === 'Bekor qilindi') {
    return { cls: 'cancelled', dotText: t('status_cancelled'), sub: t('status_cancelled_sub') };
  }
  return { cls: 'in-progress', dotText: status, sub: '' };
}

function renderOrdersGrid() {
  const container = document.getElementById('orders-grid');
  if (!container) return;

  // Filter orders
  let filtered = state.orders.filter(order => {
    // Status Filter
    if (state.orderStatusFilter === 'process') {
      if (order.status !== 'Kutilmoqda' && order.status !== 'Tayyorlanmoqda') return false;
    } else if (state.orderStatusFilter === 'completed') {
      if (order.status !== 'Tasdiqlandi' && order.status !== 'Tugatildi') return false;
    } else if (state.orderStatusFilter === 'cancelled') {
      if (order.status !== 'Bekor qilindi') return false;
    }

    // Search query filter
    if (state.searchQuery) {
      const q = state.searchQuery;
      const phoneMatch = (order.user_phone || '').toLowerCase().includes(q);
      const idMatch = `#${order.id}`.includes(q) || String(order.id).includes(q);
      const addressMatch = (order.address || '').toLowerCase().includes(q);
      const itemsMatch = (order.items || []).some(item => (item.name || '').toLowerCase().includes(q));
      if (!phoneMatch && !idMatch && !addressMatch && !itemsMatch) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #94A3B8;">
        <div style="font-size: 48px; margin-bottom: 12px;">🧾</div>
        <h3 style="font-size: 18px; color: #475569; margin-bottom: 6px;">${t('no_orders_found')}</h3>
        <p style="font-size: 13px;">${t('no_orders_sub')}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map((order, idx) => {
    const badge = getOrderBadgeInfo(order, idx);
    const statusInfo = getStatusPillInfo(order.status);
    const isExpanded = state.expandedOrders.has(order.id);
    const displayItems = isExpanded ? order.items : (order.items || []).slice(0, 3);
    const hasMore = (order.items || []).length > 3 && !isExpanded;
    const remainingCount = (order.items || []).length - 3;
    const paymentText = order.payment_method === 'Karta' ? t('card') : t('cash');

    return `
      <div class="order-card ${order.status === 'Kutilmoqda' ? 'new-order-highlight' : ''}" id="order-card-${order.id}">
        <div>
          <!-- Header -->
          <div class="card-header">
            <div class="customer-group">
              <div class="table-badge ${badge.colorClass}">${badge.text}</div>
              <div class="customer-meta">
                <div class="customer-name">${order.user_phone || 'Mijoz'}</div>
                <div class="order-type-sub">${t('order')} #${order.id} • ${badge.subtext}</div>
              </div>
            </div>
            <div class="status-pill ${statusInfo.cls}">
              <span class="dot"></span>
              <span>${statusInfo.dotText}</span>
            </div>
          </div>

          <!-- Time & Date -->
          <div class="card-time-row" style="margin-top: 12px;">
            <span>${order.created_date || 'Bugun'}</span>
            <span>${order.created_time || '18:00'}</span>
          </div>

          <!-- Items Table -->
          <div class="items-list-container" style="margin-top: 10px;">
            <div class="items-header">
              <span>${t('dishes_col')}</span>
              <span style="text-align: center;">${t('qty_col')}</span>
              <span style="text-align: right;">${t('price_col')}</span>
            </div>
            ${displayItems.map(item => {
              const matched = state.menuItems.find(m => m.id === item.menu_item_id || m.name === item.name);
              const displayName = matched ? getDishName(matched) : item.name;
              return `
              <div class="item-row">
                <span class="item-name" title="${displayName}">${displayName}</span>
                <span class="item-qty">${item.quantity}</span>
                <span class="item-price">${formatPrice(item.price * item.quantity)}</span>
              </div>
            `;}).join('')}
            ${hasMore ? `
              <button class="more-items-btn" onclick="toggleExpandOrder(${order.id})">+${remainingCount} ${t('more_items')}</button>
            ` : ''}
          </div>

          <!-- Badges (Payment & Address & Promocode) -->
          <div class="card-badges-row" style="margin-top: 10px;">
            <span class="card-info-tag">
              <span>💳</span> <span>${paymentText}</span>
            </span>
            ${order.promocode ? `
              <span class="card-info-tag" style="background: rgba(16, 185, 129, 0.15); border-color: #10B981; color: #10B981; font-weight: 700;">
                <span>🎟️</span> <span>${order.promocode}</span>
              </span>
            ` : ''}
            ${order.receipt_image ? `
              <span class="card-info-tag receipt-attached" onclick="openReceiptModal('/static/uploads/receipts/${order.receipt_image}')">
                <span>📎</span> <span>${t('receipt_attached')}</span>
              </span>
            ` : ''}
            ${order.address ? `
              <span class="card-info-tag" title="${order.address}">
                <span>📍</span> <span>${order.address.length > 25 ? order.address.substring(0, 25) + '...' : order.address}</span>
              </span>
            ` : ''}
          </div>
        </div>

        <!-- Footer / Total & Actions -->
        <div class="card-footer-box">
          <div class="total-row">
            <span class="total-label">${t('total_lbl')}</span>
            <span class="total-amount">${formatPrice(order.total_amount)}</span>
          </div>
          <div class="card-actions-row">
            <button class="btn-card-secondary" style="flex: 1;" onclick="openOrderDetailsModal(${order.id})">${t('see_details')}</button>
            ${order.status === 'Kutilmoqda' ? `
              <button class="btn-card-primary" style="flex: 1;" onclick="quickUpdateStatus(${order.id}, 'Tasdiqlandi')">${t('pay_bills')}</button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');
}

function toggleExpandOrder(orderId) {
  if (state.expandedOrders.has(orderId)) {
    state.expandedOrders.delete(orderId);
  } else {
    state.expandedOrders.add(orderId);
  }
  renderOrdersGrid();
}

async function quickUpdateStatus(orderId, newStatus) {
  try {
    const res = await fetch(`/api/admin/orders/${orderId}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('order_status_updated'), 'success');
      fetchOrders(false);
    } else {
      showToast(data.error || "Error updating status", "error");
    }
  } catch (err) {
    showToast("Server connection error", "error");
  }
}

// ==========================================================================
// PAYMENT / ORDER DETAILS MODAL WITH NUMPAD
// ==========================================================================

function openOrderDetailsModal(orderId) {
  const order = state.orders.find(o => o.id === orderId);
  if (!order) return;

  state.selectedOrder = order;
  state.calcInput = String(order.total_amount || 0);

  // Fill in receipt details
  const modalBadge = document.getElementById('modal-order-badge');
  const modalCustomerName = document.getElementById('modal-customer-name');
  const modalCustomerPhone = document.getElementById('modal-customer-phone');
  const modalOrderType = document.getElementById('modal-order-type');
  const modalAddress = document.getElementById('modal-order-address');
  const modalItemsTable = document.getElementById('modal-items-tbody');
  const modalSubtotal = document.getElementById('modal-subtotal');
  const modalGrandTotal = document.getElementById('modal-grandtotal');
  const modalReceiptBox = document.getElementById('modal-receipt-box');

  const badge = getOrderBadgeInfo(order, 0);
  if (modalBadge) {
    modalBadge.className = `table-badge ${badge.colorClass}`;
    modalBadge.textContent = badge.text;
  }
  if (modalCustomerName) modalCustomerName.textContent = order.user_phone || 'Mijoz';
  if (modalCustomerPhone) modalCustomerPhone.innerHTML = `<a href="tel:${order.user_phone}" style="color: inherit; text-decoration: none;">📞 ${order.user_phone || 'N/A'}</a>`;
  const promoStr = order.promocode ? ` • 🎟️ ${order.promocode}` : '';
  if (modalOrderType) modalOrderType.textContent = `${t('order')} #${order.id} (${order.payment_method === 'Karta' ? t('card') : t('cash')})${promoStr}`;
  if (modalAddress) {
    modalAddress.innerHTML = `📍 <strong>${t('address_lbl')}</strong> ${order.address || t('not_specified')} ` +
      (order.latitude && order.longitude ? `<a href="https://maps.google.com/?q=${order.latitude},${order.longitude}" target="_blank" style="color: #0284C7; margin-left: 8px;">${t('view_map')}</a>` : '');
  }

  // Items
  if (modalItemsTable) {
    modalItemsTable.innerHTML = (order.items || []).map(item => {
      const matched = state.menuItems.find(m => m.id === item.menu_item_id || m.name === item.name);
      const displayName = matched ? getDishName(matched) : item.name;
      return `
      <tr>
        <td style="font-weight: 600;">${displayName}</td>
        <td style="text-align: center; color: var(--text-muted);">${item.quantity}x</td>
        <td style="text-align: right; font-weight: 700;">${formatPrice(item.price * item.quantity)}</td>
      </tr>
    `;}).join('');
  }

  if (modalSubtotal) modalSubtotal.textContent = formatPrice(order.total_amount);
  if (modalGrandTotal) modalGrandTotal.textContent = formatPrice(order.total_amount);

  // Receipt image check
  if (modalReceiptBox) {
    if (order.receipt_image) {
      modalReceiptBox.style.display = 'block';
      modalReceiptBox.innerHTML = `
        <div style="background: rgba(255, 192, 67, 0.15); border: 1px solid var(--border-gold); padding: 12px; border-radius: 10px; display: flex; align-items: center; justify-content: space-between;">
          <span style="font-size: 13px; font-weight: 700; color: var(--gold-dark);">${t('modal_card_receipt_alert')}</span>
          <button style="padding: 6px 14px; background: #FFC043; color: #1E293B; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;" onclick="openReceiptModal('/static/uploads/receipts/${order.receipt_image}')">${t('modal_view_receipt')}</button>
        </div>
      `;
    } else {
      modalReceiptBox.style.display = 'none';
    }
  }

  // Action buttons visibility in modal
  const btnPayNow = document.getElementById('modal-btn-pay-now');
  const btnCancel = document.getElementById('modal-btn-cancel-order');
  
  if (btnPayNow) {
    // If order is already confirmed / completed / cancelled, HIDE Tasdiqlash button
    if (order.status !== 'Kutilmoqda') {
      btnPayNow.style.display = 'none';
    } else {
      btnPayNow.style.display = 'flex';
    }
  }

  if (btnCancel) {
    if (order.status === 'Bekor qilindi') {
      btnCancel.style.display = 'none';
    } else {
      btnCancel.style.display = 'flex';
    }
  }

  // Open Modal
  const overlay = document.getElementById('payment-modal-overlay');
  if (overlay) overlay.classList.add('active');
}

function closeOrderDetailsModal() {
  const overlay = document.getElementById('payment-modal-overlay');
  if (overlay) overlay.classList.remove('active');
  state.selectedOrder = null;
}

async function confirmPaymentAndClose() {
  if (!state.selectedOrder) return;
  const orderId = state.selectedOrder.id;
  await quickUpdateStatus(orderId, 'Tasdiqlandi');
  closeOrderDetailsModal();
}

async function cancelOrderFromModal() {
  if (!state.selectedOrder) return;
  if (!confirm(t('order_cancelled_confirm'))) return;
  const orderId = state.selectedOrder.id;
  await quickUpdateStatus(orderId, 'Bekor qilindi');
  closeOrderDetailsModal();
}

// Receipt Image Modal
function openReceiptModal(imageUrl) {
  const modal = document.getElementById('receipt-view-modal');
  const img = document.getElementById('receipt-full-image');
  if (modal && img) {
    img.src = imageUrl;
    modal.classList.add('active');
  }
}

function closeReceiptModal() {
  const modal = document.getElementById('receipt-view-modal');
  if (modal) modal.classList.remove('active');
}

// ==========================================================================
// MENU & DISHES MANAGEMENT
// ==========================================================================

async function fetchMenuAndCategories() {
  try {
    const [resMenu, resCat] = await Promise.all([
      fetch('/api/admin/menu'),
      fetch('/api/admin/categories')
    ]);
    const menuData = await resMenu.json();
    const catData = await resCat.json();

    if (menuData.success) state.menuItems = menuData.menu || [];
    if (catData.success) state.categories = catData.categories || [];
  } catch (err) {
    console.error("Error fetching menu/categories:", err);
  }
}

function renderMenuView() {
  const container = document.getElementById('menu-grid-container');
  const catFilterContainer = document.getElementById('menu-category-filter-pills');
  if (!container) return;

  // Render category filter pills
  if (catFilterContainer) {
    catFilterContainer.innerHTML = `
      <button class="tab-btn active" onclick="filterMenuByCategory(null, this)">${t('all_categories')}</button>
      ${state.categories.map(c => `
        <button class="tab-btn" onclick="filterMenuByCategory(${c.id}, this)">${c.name}</button>
      `).join('')}
    `;
  }

  renderMenuGridFiltered(null);
}

function filterMenuByCategory(catId, btnElement) {
  if (btnElement) {
    document.querySelectorAll('#menu-category-filter-pills .tab-btn').forEach(b => b.classList.remove('active'));
    btnElement.classList.add('active');
  }
  renderMenuGridFiltered(catId);
}

function renderMenuGridFiltered(catId) {
  const container = document.getElementById('menu-grid-container');
  if (!container) return;

  let items = state.menuItems;
  if (catId) {
    items = items.filter(i => i.category_id === catId);
  }
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    items = items.filter(i => 
      (getDishName(i) || '').toLowerCase().includes(q) || 
      (getDishDesc(i) || '').toLowerCase().includes(q) ||
      (i.name || '').toLowerCase().includes(q)
    );
  }

  if (items.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
        <p>${t('no_orders_found')}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = items.map(dish => {
    const cat = state.categories.find(c => c.id === dish.category_id);
    const dName = getDishName(dish);
    const dDesc = getDishDesc(dish);
    const cName = cat ? getCategoryName(cat) : 'Umumiy';
    return `
      <div class="menu-card">
        <div class="menu-img-wrap">
          <img src="${dish.image_url || 'https://via.placeholder.com/300x200?text=No+Photo'}" alt="${dName}" onerror="this.src='https://via.placeholder.com/300x200?text=Food'">
          <span class="menu-category-tag">${cName}</span>
        </div>
        <div class="menu-body">
          <div>
            <h4 class="menu-name">${dName}</h4>
            <p class="menu-desc">${dDesc || ''}</p>
          </div>
          <div>
            ${dish.calories && dish.calories > 0 ? `<div style="margin-bottom: 6px;"><span style="display: inline-flex; align-items: center; gap: 3px; font-size: 11px; font-weight: 700; color: #F59E0B; background: rgba(245, 158, 11, 0.12); padding: 2px 7px; border-radius: 6px;">🔥 ${dish.calories} kkal</span></div>` : ''}
            <div class="menu-prices-row">
              <span class="price-current">${formatPrice(dish.price)}</span>
              ${dish.old_price && dish.old_price > 0 ? `<span class="price-old">${formatPrice(dish.old_price)}</span>` : ''}
            </div>
            <div class="menu-card-actions">
              <button class="btn-card-secondary" style="flex: 1;" onclick="openDishModal(${dish.id})">${t('edit_btn')}</button>
              <button class="btn-card-secondary" style="color: #DC2626;" onclick="deleteDish(${dish.id})">${t('delete_btn')}</button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Auto-Translation Functions
async function autoTranslateDishName() {
  const name = document.getElementById('dish-name') ? document.getElementById('dish-name').value.trim() : '';
  if (!name) return;
  const nameRuEl = document.getElementById('dish-name-ru');
  const nameEnEl = document.getElementById('dish-name-en');
  if (nameRuEl && nameEnEl && (!nameRuEl.value || !nameEnEl.value)) {
    try {
      const res = await fetch('/api/admin/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: name })
      });
      const data = await res.json();
      if (data.success && data.translations) {
        if (!nameRuEl.value && data.translations.ru) nameRuEl.value = data.translations.ru;
        if (!nameEnEl.value && data.translations.en) nameEnEl.value = data.translations.en;
      }
    } catch (err) {
      console.error("Auto translate name error:", err);
    }
  }
}

async function autoTranslateDishDesc() {
  const desc = document.getElementById('dish-description') ? document.getElementById('dish-description').value.trim() : '';
  if (!desc) return;
  const descRuEl = document.getElementById('dish-description-ru');
  const descEnEl = document.getElementById('dish-description-en');
  if (descRuEl && descEnEl && (!descRuEl.value || !descEnEl.value)) {
    try {
      const res = await fetch('/api/admin/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: desc })
      });
      const data = await res.json();
      if (data.success && data.translations) {
        if (!descRuEl.value && data.translations.ru) descRuEl.value = data.translations.ru;
        if (!descEnEl.value && data.translations.en) descEnEl.value = data.translations.en;
      }
    } catch (err) {
      console.error("Auto translate desc error:", err);
    }
  }
}

async function autoTranslateDish() {
  const name = document.getElementById('dish-name') ? document.getElementById('dish-name').value.trim() : '';
  const desc = document.getElementById('dish-description') ? document.getElementById('dish-description').value.trim() : '';
  const nameRuEl = document.getElementById('dish-name-ru');
  const nameEnEl = document.getElementById('dish-name-en');
  const descRuEl = document.getElementById('dish-description-ru');
  const descEnEl = document.getElementById('dish-description-en');

  if (!name && !desc) {
    showToast("Taom nomini kiriting!", "error");
    return;
  }

  showToast("Tarjima qilinmoqda... ⏳", "info");

  if (name && nameRuEl && nameEnEl) {
    try {
      const res = await fetch('/api/admin/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: name })
      });
      const data = await res.json();
      if (data.success && data.translations) {
        nameRuEl.value = data.translations.ru || name;
        nameEnEl.value = data.translations.en || name;
      }
    } catch (e) {}
  }

  if (desc && descRuEl && descEnEl) {
    try {
      const res = await fetch('/api/admin/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: desc })
      });
      const data = await res.json();
      if (data.success && data.translations) {
        descRuEl.value = data.translations.ru || desc;
        descEnEl.value = data.translations.en || desc;
      }
    } catch (e) {}
  }

  showToast("Avtomatik tarjima qilindi! ✓", "success");
}

// Dish Create / Edit Modal
function openDishModal(dishId = null) {
  const modal = document.getElementById('dish-modal-overlay');
  const title = document.getElementById('dish-modal-title');
  const form = document.getElementById('dish-form');
  const catSelect = document.getElementById('dish-category-select');

  // Populate categories dropdown
  if (catSelect) {
    catSelect.innerHTML = state.categories.map(c => `<option value="${c.id}">${getCategoryName(c)}</option>`).join('');
  }

  if (dishId) {
    const dish = state.menuItems.find(d => d.id === dishId);
    if (!dish) return;
    title.textContent = t('edit_dish_modal_title');
    document.getElementById('dish-id').value = dish.id;
    document.getElementById('dish-name').value = dish.name || '';
    const nameRuEl = document.getElementById('dish-name-ru');
    if (nameRuEl) nameRuEl.value = dish.name_ru || '';
    const nameEnEl = document.getElementById('dish-name-en');
    if (nameEnEl) nameEnEl.value = dish.name_en || '';
    document.getElementById('dish-price').value = dish.price;
    document.getElementById('dish-old-price').value = dish.old_price || '';
    const calEl = document.getElementById('dish-calories');
    if (calEl) calEl.value = dish.calories || '';
    document.getElementById('dish-description').value = dish.description || '';
    const descRuEl = document.getElementById('dish-description-ru');
    if (descRuEl) descRuEl.value = dish.description_ru || '';
    const descEnEl = document.getElementById('dish-description-en');
    if (descEnEl) descEnEl.value = dish.description_en || '';
    document.getElementById('dish-image-url').value = dish.image_url || '';
    if (catSelect) catSelect.value = dish.category_id;
  } else {
    title.textContent = t('add_dish_modal_title');
    form.reset();
    document.getElementById('dish-id').value = '';
    const calEl = document.getElementById('dish-calories');
    if (calEl) calEl.value = '';
  }

  if (modal) modal.classList.add('active');
}

function closeDishModal() {
  const modal = document.getElementById('dish-modal-overlay');
  if (modal) modal.classList.remove('active');
}

async function saveDish(e) {
  e.preventDefault();
  const id = document.getElementById('dish-id').value;
  const name = document.getElementById('dish-name').value.trim();
  const name_ru = document.getElementById('dish-name-ru') ? document.getElementById('dish-name-ru').value.trim() : '';
  const name_en = document.getElementById('dish-name-en') ? document.getElementById('dish-name-en').value.trim() : '';
  const price = parseInt(document.getElementById('dish-price').value, 10) || 0;
  const old_price = parseInt(document.getElementById('dish-old-price').value, 10) || 0;
  const calories = document.getElementById('dish-calories') ? (parseInt(document.getElementById('dish-calories').value, 10) || 0) : 0;
  const category_id = parseInt(document.getElementById('dish-category-select').value, 10) || 1;
  const description = document.getElementById('dish-description').value.trim();
  const description_ru = document.getElementById('dish-description-ru') ? document.getElementById('dish-description-ru').value.trim() : '';
  const description_en = document.getElementById('dish-description-en') ? document.getElementById('dish-description-en').value.trim() : '';
  const image_url = document.getElementById('dish-image-url').value.trim();

  const payload = { 
    name, 
    name_ru: name_ru || name, 
    name_en: name_en || name, 
    price, 
    old_price, 
    calories,
    category_id, 
    description, 
    description_ru: description_ru || description, 
    description_en: description_en || description, 
    image_url 
  };
  const endpoint = id ? `/api/admin/menu/${id}/update` : '/api/admin/menu/create';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('dish_saved'), "success");
      closeDishModal();
      await fetchMenuAndCategories();
      renderMenuView();
    } else {
      showToast(data.error || "Error", "error");
    }
  } catch (err) {
    showToast("Server connection error", "error");
  }
}

async function deleteDish(dishId) {
  if (!confirm(t('dish_deleted') + "?")) return;
  try {
    const res = await fetch(`/api/admin/menu/${dishId}/delete`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(t('dish_deleted'), "success");
      await fetchMenuAndCategories();
      renderMenuView();
    }
  } catch (err) {
    showToast("Error deleting dish", "error");
  }
}

// Upload Image helper
async function uploadDishImage(fileInput) {
  const file = fileInput.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('image', file);

  try {
    showToast(t('img_uploading'), "info");
    const res = await fetch('/api/admin/upload_image', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    if (data.success && data.image_url) {
      document.getElementById('dish-image-url').value = data.image_url;
      showToast(t('img_uploaded'), "success");
    } else {
      showToast(data.error || "Upload error", "error");
    }
  } catch (err) {
    showToast("Upload server error", "error");
  }
}

// ==========================================================================
// CATEGORIES MANAGEMENT (WITH DEDICATED MODAL)
// ==========================================================================

function renderCategoriesView() {
  const container = document.getElementById('categories-list-container');
  if (!container) return;

  container.innerHTML = state.categories.map(cat => {
    const count = state.menuItems.filter(m => m.category_id === cat.id).length;
    const catDisplayName = getCategoryName(cat);
    return `
      <div class="stat-card" style="justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 14px;">
          <div class="stat-icon yellow">📁</div>
          <div>
            <h4 style="font-size: 16px; font-weight: 700;">${catDisplayName}</h4>
            <span style="font-size: 12px; color: var(--text-muted);">${count} ${t('cat_dishes_count')}</span>
          </div>
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="btn-card-secondary" style="padding: 6px 12px;" onclick="openCategoryModal(${cat.id})">✏️</button>
          <button class="btn-card-secondary" style="padding: 6px 12px; color: #DC2626;" onclick="deleteCategory(${cat.id})">🗑️</button>
        </div>
      </div>
    `;
  }).join('');
}

function openCategoryModal(catId = null) {
  const modal = document.getElementById('category-modal-overlay');
  const title = document.getElementById('category-modal-title');
  const idInput = document.getElementById('category-id');
  const nameInput = document.getElementById('category-name-input');
  const nameRuInput = document.getElementById('category-name-ru-input');
  const nameEnInput = document.getElementById('category-name-en-input');

  if (catId) {
    const cat = state.categories.find(c => c.id === catId);
    title.textContent = t('edit_cat_modal_title');
    idInput.value = catId;
    nameInput.value = cat ? (cat.name || '') : '';
    if (nameRuInput) nameRuInput.value = cat ? (cat.name_ru || '') : '';
    if (nameEnInput) nameEnInput.value = cat ? (cat.name_en || '') : '';
  } else {
    title.textContent = t('add_cat_modal_title');
    idInput.value = '';
    nameInput.value = '';
    if (nameRuInput) nameRuInput.value = '';
    if (nameEnInput) nameEnInput.value = '';
  }

  if (modal) modal.classList.add('active');
  setTimeout(() => nameInput && nameInput.focus(), 100);
}

function closeCategoryModal() {
  const modal = document.getElementById('category-modal-overlay');
  if (modal) modal.classList.remove('active');
}

async function autoTranslateCategory(isExplicit = false) {
  const name = document.getElementById('category-name-input') ? document.getElementById('category-name-input').value.trim() : '';
  if (!name) {
    if (isExplicit) showToast("Kategoriya nomini kiriting!", "error");
    return;
  }
  const nameRuEl = document.getElementById('category-name-ru-input');
  const nameEnEl = document.getElementById('category-name-en-input');
  if (nameRuEl && nameEnEl && (isExplicit || !nameRuEl.value || !nameEnEl.value)) {
    if (isExplicit) showToast("Tarjima qilinmoqda... ⏳", "info");
    try {
      const res = await fetch('/api/admin/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: name })
      });
      const data = await res.json();
      if (data.success && data.translations) {
        if (isExplicit || !nameRuEl.value) nameRuEl.value = data.translations.ru || name;
        if (isExplicit || !nameEnEl.value) nameEnEl.value = data.translations.en || name;
        if (isExplicit) showToast("Avtomatik tarjima qilindi! ✓", "success");
      }
    } catch (err) {
      console.error("Auto translate category error:", err);
    }
  }
}

async function saveCategoryForm(e) {
  e.preventDefault();
  const id = document.getElementById('category-id').value;
  const name = document.getElementById('category-name-input').value.trim();
  const name_ru = document.getElementById('category-name-ru-input') ? document.getElementById('category-name-ru-input').value.trim() : '';
  const name_en = document.getElementById('category-name-en-input') ? document.getElementById('category-name-en-input').value.trim() : '';

  if (!name) return;

  const payload = { name, name_ru: name_ru || '', name_en: name_en || '' };
  const endpoint = id ? `/api/admin/category/${id}/update` : '/api/admin/category/create';

  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('category_saved'), "success");
      closeCategoryModal();
      await fetchMenuAndCategories();
      renderCategoriesView();
      if (state.currentTab === 'menu') renderMenuView();
    } else {
      showToast(data.error || "Error", "error");
    }
  } catch (err) {
    showToast("Server connection error", "error");
  }
}

async function deleteCategory(id) {
  if (!confirm(t('category_deleted') + "?")) return;
  try {
    const res = await fetch(`/api/admin/category/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(t('category_deleted'), "success");
      await fetchMenuAndCategories();
      renderCategoriesView();
    }
  } catch (err) {
    showToast("Error deleting category", "error");
  }
}

// ==========================================================================
// PROMOTIONS MANAGEMENT
// ==========================================================================

async function fetchPromotions() {
  try {
    const res = await fetch('/api/admin/promotions');
    const data = await res.json();
    if (data.success) {
      state.promotions = data.promotions || [];
      renderPromotionsView();
    }
  } catch (err) {
    console.error("Error fetching promotions:", err);
  }
}

function renderPromotionsView() {
  const container = document.getElementById('promotions-grid-container');
  if (!container) return;

  if (state.promotions.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
        <p>${t('no_orders_found')}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.promotions.map(p => {
    const pTitle = getPromoTitle(p);
    const pDesc = getPromoDesc(p);
    return `
      <div class="stat-card" style="flex-direction: column; align-items: stretch; gap: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="status-pill ${p.is_active ? 'ready' : 'cancelled'}">
            <span class="dot"></span>
            <span>${p.is_active ? t('active_promo') : t('inactive_promo')}</span>
          </span>
          <span style="font-size: 16px; font-weight: 800; color: #D97706;">-${p.discount_percent}%</span>
        </div>
        <div>
          <h4 style="font-size: 16px; font-weight: 700; margin-bottom: 4px;">${pTitle}</h4>
          <p style="font-size: 13px; color: var(--text-muted);">${pDesc || ''}</p>
          <div style="font-size: 11px; color: var(--text-light); margin-top: 6px;">${t('end_date_lbl')} ${p.end_date || t('not_specified')}</div>
        </div>
        <div style="display: flex; gap: 8px; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
          <button class="btn-card-secondary" style="flex: 1;" onclick="togglePromoStatus(${p.id})">
            ${p.is_active ? t('turn_off') : t('turn_on')}
          </button>
          <button class="btn-card-secondary" style="color: #DC2626;" onclick="deletePromo(${p.id})">🗑️</button>
        </div>
      </div>
    `;
  }).join('');
}

function openPromotionModal() {
  const modal = document.getElementById('promo-modal-overlay');
  if (modal) modal.classList.add('active');
}

function closePromotionModal() {
  const modal = document.getElementById('promo-modal-overlay');
  if (modal) modal.classList.remove('active');
}

async function savePromotion(e) {
  e.preventDefault();
  const title = document.getElementById('promo-title').value.trim();
  const title_ru = document.getElementById('promo-title-ru') ? document.getElementById('promo-title-ru').value.trim() : '';
  const title_en = document.getElementById('promo-title-en') ? document.getElementById('promo-title-en').value.trim() : '';
  const description = document.getElementById('promo-desc').value.trim();
  const description_ru = document.getElementById('promo-desc-ru') ? document.getElementById('promo-desc-ru').value.trim() : '';
  const description_en = document.getElementById('promo-desc-en') ? document.getElementById('promo-desc-en').value.trim() : '';
  const discount_percent = parseInt(document.getElementById('promo-discount').value, 10) || 0;
  const end_date = document.getElementById('promo-end-date').value;

  try {
    const res = await fetch('/api/admin/promotion/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        title, 
        title_ru: title_ru || title, 
        title_en: title_en || title, 
        description, 
        description_ru: description_ru || description, 
        description_en: description_en || description, 
        discount_percent, 
        end_date 
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('promo_saved'), "success");
      closePromotionModal();
      fetchPromotions();
    }
  } catch (err) {
    showToast("Error saving promo", "error");
  }
}

async function togglePromoStatus(id) {
  try {
    const res = await fetch(`/api/admin/promotion/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(t('order_status_updated'), "success");
      fetchPromotions();
    }
  } catch (err) {
    showToast("Error deleting promo", "error");
  }
}

// Sub-Tab Switcher for Discounts View (Aksiyalar vs Promokodlar)
function switchPromoSubTab(subTab) {
  state.promoSubTab = subTab;
  const btnPromos = document.getElementById('subtab-promos');
  const btnPromocodes = document.getElementById('subtab-promocodes');
  const gridPromos = document.getElementById('promotions-grid-container');
  const gridPromocodes = document.getElementById('promocodes-grid-container');
  const actionBtn = document.getElementById('header-action-btn');

  if (btnPromos) btnPromos.classList.toggle('active', subTab === 'promos');
  if (btnPromocodes) btnPromocodes.classList.toggle('active', subTab === 'promocodes');

  if (subTab === 'promos') {
    if (gridPromos) gridPromos.style.display = 'grid';
    if (gridPromocodes) gridPromocodes.style.display = 'none';
    if (actionBtn) {
      actionBtn.innerHTML = `<span>➕</span> <span>${t('add_discount')}</span>`;
      actionBtn.onclick = () => openPromotionModal();
    }
    fetchPromotions();
  } else {
    if (gridPromos) gridPromos.style.display = 'none';
    if (gridPromocodes) gridPromocodes.style.display = 'grid';
    if (actionBtn) {
      actionBtn.innerHTML = `<span>➕</span> <span>${t('add_promocode')}</span>`;
      actionBtn.onclick = () => openPromoCodeModal();
    }
    fetchPromoCodes();
  }
}

// Promocodes CRUD
async function fetchPromoCodes() {
  try {
    const res = await fetch('/api/admin/promocodes');
    const data = await res.json();
    if (data.success) {
      state.promocodes = data.promocodes || [];
      renderPromoCodesView();
    }
  } catch (err) {
    console.error("Error fetching promocodes:", err);
  }
}

function renderPromoCodesView() {
  const container = document.getElementById('promocodes-grid-container');
  if (!container) return;

  if (state.promocodes.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted);">
        <p>${t('no_promocodes_found')}</p>
      </div>
    `;
    return;
  }

  container.innerHTML = state.promocodes.map(p => {
    let rangeText = t('promo_all_orders');
    if (p.min_order_amount > 0 && p.max_order_amount > 0) {
      rangeText = `${formatPrice(p.min_order_amount)} — ${formatPrice(p.max_order_amount)}`;
    } else if (p.min_order_amount > 0) {
      rangeText = `Min. ${formatPrice(p.min_order_amount)}`;
    } else if (p.max_order_amount > 0) {
      rangeText = `Maks. ${formatPrice(p.max_order_amount)}`;
    }

    const expiryText = p.end_date ? `⏳ ${p.end_date}` : `⏳ ${t('promo_unlimited')}`;

    return `
      <div class="stat-card" style="flex-direction: column; align-items: stretch; gap: 14px; position: relative;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span class="status-pill ${p.is_active ? 'ready' : 'cancelled'}">
            <span class="dot"></span>
            <span>${p.is_active ? t('active_promo') : t('inactive_promo')}</span>
          </span>
          <span style="font-size: 18px; font-weight: 800; color: #10B981;">-${p.discount_percent}%</span>
        </div>
        <div>
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="font-size: 20px;">🎟️</span>
            <span style="font-size: 20px; font-weight: 800; font-family: monospace; letter-spacing: 1.5px; color: var(--gold);">${p.code}</span>
          </div>
          <div style="display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--text-muted);">
            <div>💳 <strong>${t('promo_range_lbl')}</strong> ${rangeText}</div>
            <div>${expiryText}</div>
            <div style="margin-top: 2px;">📊 ${p.times_used} ${t('times_used_suffix')}</div>
          </div>
        </div>
        <div style="display: flex; gap: 8px; border-top: 1px solid var(--border-subtle); padding-top: 10px;">
          <button class="btn-card-secondary" style="flex: 1;" onclick="togglePromoCodeStatus(${p.id})">
            ${p.is_active ? t('turn_off') : t('turn_on')}
          </button>
          <button class="btn-card-secondary" style="color: #DC2626;" onclick="deletePromoCode(${p.id})">🗑️</button>
        </div>
      </div>
    `;
  }).join('');
}

function openPromoCodeModal() {
  const modal = document.getElementById('promocode-modal-overlay');
  const codeInput = document.getElementById('promocode-code-input');
  const discInput = document.getElementById('promocode-discount-input');
  const endDateInput = document.getElementById('promocode-end-date');
  const minInput = document.getElementById('promocode-min-amount');
  const maxInput = document.getElementById('promocode-max-amount');

  if (codeInput) codeInput.value = '';
  if (discInput) discInput.value = '3';
  if (endDateInput) endDateInput.value = '';
  if (minInput) minInput.value = '';
  if (maxInput) maxInput.value = '';

  if (modal) modal.classList.add('active');
  setTimeout(() => codeInput && codeInput.focus(), 100);
}

function closePromoCodeModal() {
  const modal = document.getElementById('promocode-modal-overlay');
  if (modal) modal.classList.remove('active');
}

async function savePromoCodeForm(e) {
  e.preventDefault();
  const code = document.getElementById('promocode-code-input').value.trim().toUpperCase();
  const discount_percent = parseInt(document.getElementById('promocode-discount-input').value, 10) || 0;
  const end_date = document.getElementById('promocode-end-date') ? document.getElementById('promocode-end-date').value.trim() : '';
  const min_order_amount = document.getElementById('promocode-min-amount') ? (parseInt(document.getElementById('promocode-min-amount').value, 10) || 0) : 0;
  const max_order_amount = document.getElementById('promocode-max-amount') ? (parseInt(document.getElementById('promocode-max-amount').value, 10) || 0) : 0;

  if (!code) {
    showToast("Promokod kodini kiriting!", "error");
    return;
  }

  try {
    const res = await fetch('/api/admin/promocode/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        code,
        discount_percent,
        end_date,
        min_order_amount,
        max_order_amount
      })
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('promocode_saved'), "success");
      closePromoCodeModal();
      fetchPromoCodes();
    } else {
      showToast(data.error || "Error", "error");
    }
  } catch (err) {
    showToast("Server connection error", "error");
  }
}

async function togglePromoCodeStatus(id) {
  try {
    const res = await fetch(`/api/admin/promocode/${id}/toggle`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(t('order_status_updated'), "success");
      fetchPromoCodes();
    }
  } catch (err) {
    showToast("Error", "error");
  }
}

async function deletePromoCode(id) {
  if (!confirm(t('promocode_deleted') + "?")) return;
  try {
    const res = await fetch(`/api/admin/promocode/${id}/delete`, { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast(t('promocode_deleted'), "success");
      fetchPromoCodes();
    }
  } catch (err) {
    showToast("Error deleting promocode", "error");
  }
}

// ==========================================================================
// ACCOUNTING & STATS
// ==========================================================================

async function fetchStats() {
  try {
    const res = await fetch('/api/admin/stats');
    const data = await res.json();
    if (data.success) {
      state.stats = data.stats || {};
      renderStatsView();
    }
  } catch (err) {
    console.error("Error fetching stats:", err);
  }
}

function renderStatsView() {
  const stats = state.stats;
  document.getElementById('stat-today-revenue').textContent = formatPrice(stats.today_revenue || 0);
  document.getElementById('stat-today-orders').textContent = (stats.today_orders || 0) + (state.lang === 'en' ? " orders" : " ta");
  document.getElementById('stat-avg-order').textContent = formatPrice(stats.avg_order || 0);
  document.getElementById('stat-pending-orders').textContent = (stats.pending_orders || 0) + (state.lang === 'en' ? " orders" : " ta");

  // Payment Breakdown
  document.getElementById('stat-cash-sum').textContent = formatPrice(stats.cash_revenue || 0);
  document.getElementById('stat-card-sum').textContent = formatPrice(stats.card_revenue || 0);

  // Top Dishes
  const topList = document.getElementById('stat-top-dishes-list');
  if (topList) {
    if ((stats.top_dishes || []).length === 0) {
      topList.innerHTML = `<li style="padding: 10px; color: var(--text-muted);">${t('no_sales_yet')}</li>`;
    } else {
      topList.innerHTML = stats.top_dishes.map((item, idx) => `
        <li style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border-light); font-size: 13.5px;">
          <span><strong>#${idx + 1}</strong> ${item.name}</span>
          <span style="font-weight: 700; color: var(--forest-teal);">${item.qty} ${t('sold_qty_suffix')}</span>
        </li>
      `).join('');
    }
  }
}

// ==========================================================================
// SETTINGS
// ==========================================================================

async function fetchSettings() {
  try {
    const res = await fetch('/api/admin/settings');
    const data = await res.json();
    if (data.success && data.settings) {
      state.settings = data.settings;
      const cardNum = document.getElementById('setting-card-number');
      const cardName = document.getElementById('setting-card-name');
      const workStart = document.getElementById('setting-work-start');
      const workEnd = document.getElementById('setting-work-end');

      if (cardNum) cardNum.value = data.settings.card_number || '';
      if (cardName) cardName.value = data.settings.card_name || '';
      if (workStart) workStart.value = data.settings.work_time_start || '09:00';
      if (workEnd) workEnd.value = data.settings.work_time_end || '22:00';
    }
  } catch (err) {
    console.error("Error fetching settings:", err);
  }
}

async function saveSettings(e) {
  e.preventDefault();
  const card_number = document.getElementById('setting-card-number').value.trim();
  const card_name = document.getElementById('setting-card-name').value.trim();
  const work_time_start = document.getElementById('setting-work-start').value;
  const work_time_end = document.getElementById('setting-work-end').value;

  try {
    const res = await fetch('/api/admin/settings/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ card_number, card_name, work_time_start, work_time_end })
    });
    const data = await res.json();
    if (data.success) {
      showToast(t('settings_saved'), "success");
    } else {
      showToast(data.error || "Error", "error");
    }
  } catch (err) {
    showToast("Server connection error", "error");
  }
}
