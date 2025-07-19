# keyboards.py
import math
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import database as db
import config
import locale
import ui_config
from products import calculate_credit_cost

# --- Universal Pagination Helper ---
def paginate(data: list, page: int = 1, page_size: int = 5):
    try: page = int(page)
    except (ValueError, TypeError): page = 1
    if page < 1: page = 1
    total_items = len(data)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    if page > total_pages: page = total_pages
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = data[start_index:end_index]
    return paginated_data, total_pages, page

# --- Pagination Control Row ---
def get_pagination_controls(current_page: int, total_pages: int, callback_prefix: str) -> list:
    controls = []
    if total_pages > 1:
        prev_page = InlineKeyboardButton("⬅️", callback_data=f"{callback_prefix}_{current_page - 1}")
        next_page = InlineKeyboardButton("➡️", callback_data=f"{callback_prefix}_{current_page + 1}")
        page_indicator = InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="noop")
        row = []
        if current_page > 1: row.append(prev_page)
        row.append(page_indicator)
        if current_page < total_pages: row.append(next_page)
        controls.append(row)
    return controls

# --- Navigation Keyboards ---
def get_main_menu_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(locale.get_text('main_menu_button_browse', lang), callback_data='shop_main')],
        [InlineKeyboardButton(locale.get_text('main_menu_button_buy_credits', lang), callback_data='credits_buy_start')],
        [
            InlineKeyboardButton(locale.get_text('main_menu_button_orders', lang), callback_data='orders_view_1'),
            InlineKeyboardButton(locale.get_text('main_menu_button_refresh', lang), callback_data='main_menu_refresh')
        ],
        [InlineKeyboardButton(locale.get_text('main_menu_button_language', lang), callback_data='change_lang')]
    ])

# === DEFINITIVE FIX: back_button ALWAYS returns a single button object ===
def back_button(callback_data: str, lang: str = 'en') -> InlineKeyboardButton:
    """Returns a single InlineKeyboardButton, not a list."""
    return InlineKeyboardButton(f"⬅️ {locale.get_text('back_button', lang)}", callback_data=callback_data)

# --- My Orders Paginated Keyboard ---
def get_my_orders_keyboard(paginated_orders: list, total_pages: int, current_page: int, lang: str) -> InlineKeyboardMarkup:
    keyboard = []
    pagination_row = get_pagination_controls(current_page, total_pages, callback_prefix="orders_view")
    keyboard.extend(pagination_row)
    # Correctly build the row: [[button]]
    keyboard.append([back_button('main_menu', lang)])
    return InlineKeyboardMarkup(keyboard)

# --- Admin Panel Keyboards ---
def get_user_management_keyboard(user_id: int, is_banned: bool) -> InlineKeyboardMarkup:
    ban_text = "✅ Unban User" if is_banned else "🚫 Ban User"
    ban_cb = f"admin_user_unban_{user_id}" if is_banned else f"admin_user_ban_{user_id}"
    keyboard = [
        [InlineKeyboardButton("💰 Adjust Credits", callback_data=f"admin_user_credits_{user_id}")],
        [InlineKeyboardButton(ban_text, callback_data=ban_cb)],
        [InlineKeyboardButton("🗑️ Purge User Data", callback_data=f"admin_user_purge_{user_id}")],
        [back_button("admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_broadcast_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📢 Broadcast to ALL Users", callback_data="admin_broadcast_all")],
        [InlineKeyboardButton("👤 Message a Single User", callback_data="admin_broadcast_one")],
        [back_button("admin_panel")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- Product Shopping Keyboards ---
async def get_operator_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    operators = await db.get_operators()
    keyboard = []
    for (op,) in operators:
        emoji = ui_config.OPERATOR_EMOJIS.get(op, ui_config.DEFAULT_OPERATOR_EMOJI)
        keyboard.append([InlineKeyboardButton(f"{emoji} {op}", callback_data=f"shop_op_{op}")])
    keyboard.append([back_button('main_menu', lang)])
    return InlineKeyboardMarkup(keyboard)

async def get_category_keyboard(operator: str, lang: str = 'en') -> InlineKeyboardMarkup:
    categories = await db.get_categories_for_operator(operator)
    keyboard = []
    for cat in categories:
        emoji = ui_config.CATEGORY_EMOJIS.get(cat, ui_config.DEFAULT_CATEGORY_EMOJI)
        keyboard.append([InlineKeyboardButton(f"{emoji} {cat}", callback_data=f"shop_cat_{operator}_{cat.replace(' ', '_')}_1")])
    keyboard.append([back_button('shop_main', lang)])
    return InlineKeyboardMarkup(keyboard)

async def get_product_keyboard(product_list: list, operator: str, category: str, lang: str = 'en', page: int = 1) -> InlineKeyboardMarkup:
    paginated_products, total_pages, current_page = paginate(product_list, page)
    keyboard = []
    for prod_id, name, price, extra in paginated_products:
        credits = calculate_credit_cost(price)
        extra_text = f" {extra}" if extra else ""
        button_text = f"{name}{extra_text} - {credits:.2f} C"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_prod_{prod_id}")])
    pagination_row = get_pagination_controls(current_page, total_pages, callback_prefix=f"shop_page_{operator}_{category.replace(' ', '_')}")
    keyboard.extend(pagination_row)
    keyboard.append([back_button(f"shop_op_{operator}", lang)])
    return InlineKeyboardMarkup(keyboard)

async def get_beautiful_numbers_keyboard(number_list: list, operator: str, lang: str = 'en', page: int = 1) -> InlineKeyboardMarkup:
    paginated_numbers, total_pages, current_page = paginate(number_list, page)
    keyboard = [[InlineKeyboardButton(locale.get_text('bnum_instructions_button', lang), callback_data="shop_bnum_info")]]
    for bnum_id, phone, price in paginated_numbers:
        credits = calculate_credit_cost(price)
        button_text = f"📞 {phone} - {credits:.2f} C"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"shop_bnum_{bnum_id}")])
    pagination_row = get_pagination_controls(current_page, total_pages, callback_prefix=f"shop_page_{operator}_Beautiful_Numbers")
    keyboard.extend(pagination_row)
    keyboard.append([back_button(f"shop_op_{operator}", lang)])
    return InlineKeyboardMarkup(keyboard)

def get_product_confirmation_keyboard(product_id: str, is_bnum: bool = False, lang: str = 'en') -> InlineKeyboardMarkup:
    prefix = "bnum" if is_bnum else "prod"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"✅ {locale.get_text('proceed_prompt', lang)}", callback_data=f"buy_confirm_{prefix}_{product_id}")],
        [InlineKeyboardButton(locale.get_text('cancel_button', lang), callback_data=f"buy_cancel_{prefix}_{product_id}")]
    ])

# --- Credit Purchase Keyboards ---
def get_credit_packages_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    keyboard = []
    for pkg in config.CREDIT_PACKAGES:
        keyboard.append([InlineKeyboardButton(f"{pkg['credits']} Credits - {pkg['price']:,} MMK", callback_data=f"credits_pkg_{pkg['price']}")])
    keyboard.append([InlineKeyboardButton(locale.get_text('manual_amount_button', lang), callback_data="credits_manual")])
    keyboard.append([back_button('main_menu', lang)])
    return InlineKeyboardMarkup(keyboard)

def get_payment_method_keyboard(price: int, lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 Pay with Wave Money", callback_data=f'pay_wave_{price}')],
        [InlineKeyboardButton("💳 Pay with KBZ Pay", callback_data=f'pay_kbz_{price}')],
        [back_button('credits_buy_start', lang)]
    ])

def get_cancel_flow_keyboard(lang: str = 'en') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(locale.get_text('cancel_button', lang), callback_data='cancel_flow')]])