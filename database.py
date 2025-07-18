# database.py
import aiosqlite
import sqlite3
from config import logger
from products import INITIAL_PRODUCTS

DB_NAME = 'bot_database.db'

async def setup_database():
    logger.info("Initializing and verifying database schema...")
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, credits REAL DEFAULT 0, language TEXT DEFAULT 'en', is_banned INTEGER DEFAULT 0)")
            cursor.execute("PRAGMA table_info(users)")
            columns = [c[1] for c in cursor.fetchall()]
            if 'language' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
            if 'is_banned' not in columns: cursor.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER DEFAULT 0")
            cursor.execute("CREATE TABLE IF NOT EXISTS orders (order_id TEXT PRIMARY KEY, user_id INTEGER, order_type TEXT, package_name TEXT, credit_cost REAL, payment_method TEXT, status TEXT, screenshot_file_id TEXT, delivery_info TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
            cursor.execute("CREATE TABLE IF NOT EXISTS products (product_id TEXT PRIMARY KEY, operator TEXT NOT NULL, category TEXT NOT NULL, name TEXT NOT NULL, price_mmk INTEGER NOT NULL, extra_info TEXT, is_active INTEGER DEFAULT 1)")
            cursor.execute("CREATE TABLE IF NOT EXISTS beautiful_numbers (id INTEGER PRIMARY KEY AUTOINCREMENT, operator TEXT NOT NULL, phone_number TEXT NOT NULL UNIQUE, price_mmk INTEGER NOT NULL, is_active INTEGER DEFAULT 1)")
            conn.commit()
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("SELECT COUNT(*) FROM products")
            if (await cursor.fetchone())[0] == 0:
                logger.info("Populating products table with initial data...")
                for operator, categories in INITIAL_PRODUCTS.items():
                    for category, products_list in categories.items():
                        for product in products_list:
                            await db.execute("INSERT INTO products (product_id, operator, category, name, price_mmk, extra_info) VALUES (?, ?, ?, ?, ?, ?)", (product['id'], operator, category, product['name'], product['price_mmk'], product.get('extra')))
                await db.commit()
    except Exception as e:
        logger.error(f"FATAL: Failed to initialize database: {e}", exc_info=True); raise

async def _db_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute(query, params)
            if commit: await db.commit(); return True
            if fetchone: return await cursor.fetchone()
            if fetchall: return await cursor.fetchall()
            return await cursor.fetchall()
    except aiosqlite.Error as e: logger.error(f"Database query failed: {e}\nQuery: {query}\nParams: {params}"); return None

async def get_user_data(user_id: int) -> dict:
    await _db_query("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,), commit=True)
    user_data = await _db_query("SELECT credits, language, is_banned FROM users WHERE user_id = ?", (user_id,), fetchone=True)
    return {'credits': user_data[0], 'language': user_data[1], 'is_banned': bool(user_data[2])} if user_data else {'credits': 0.0, 'language': 'en', 'is_banned': False}

async def set_user_language(user_id: int, lang_code: str):
    return await _db_query("UPDATE users SET language = ? WHERE user_id = ?", (lang_code, user_id), commit=True)

async def change_user_credits(user_id: int, amount: float):
    return await _db_query("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id), commit=True)

async def create_order(**kwargs):
    columns, placeholders = ', '.join(kwargs.keys()), ', '.join('?' * len(kwargs))
    return await _db_query(f"INSERT INTO orders ({columns}) VALUES ({placeholders})", tuple(kwargs.values()), commit=True)

async def update_order_status_and_screenshot(order_id: str, status: str, screenshot_file_id: str):
    return await _db_query("UPDATE orders SET status = ?, screenshot_file_id = ? WHERE order_id = ?", (status, screenshot_file_id, order_id), commit=True)

async def set_order_status(order_id: str, status: str):
    return await _db_query("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id), commit=True)

async def get_user_orders(user_id: int) -> tuple:
    all_orders = await _db_query("SELECT order_id, package_name, status, created_at, credit_cost FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,), fetchall=True)
    pending = [o for o in all_orders if o[2] in ('pending_approval', 'pending_payment')]
    history = [o for o in all_orders if o[2] in ('completed', 'rejected')]
    return pending, history

async def get_order_details(order_id: str):
    return await _db_query("SELECT user_id, credit_cost, package_name, status, order_type FROM orders WHERE order_id = ?", (order_id,), fetchone=True)

async def get_operators():
    return await _db_query("SELECT DISTINCT operator FROM products WHERE is_active = 1 ORDER BY operator", fetchall=True)

async def get_categories_for_operator(operator: str):
    categories, has_b_nums = await _db_query("SELECT DISTINCT category FROM products WHERE operator = ? AND is_active = 1", (operator,), fetchall=True), await _db_query("SELECT 1 FROM beautiful_numbers WHERE operator = ? AND is_active = 1 LIMIT 1", (operator,), fetchone=True)
    cat_list = [c[0] for c in categories]
    if has_b_nums: cat_list.append("Beautiful Numbers")
    return sorted(cat_list)

async def get_products_in_category(operator: str, category: str):
    return await _db_query("SELECT product_id, name, price_mmk, extra_info FROM products WHERE operator = ? AND category = ? AND is_active = 1", (operator, category), fetchall=True)

async def get_product_by_id(product_id: str):
    return await _db_query("SELECT product_id, operator, category, name, price_mmk, extra_info FROM products WHERE product_id = ?", (product_id,), fetchone=True)

async def get_beautiful_numbers(operator: str):
    return await _db_query("SELECT id, phone_number, price_mmk FROM beautiful_numbers WHERE operator = ? AND is_active = 1", (operator,), fetchall=True)

async def get_beautiful_number_by_id(b_num_id: int):
    return await _db_query("SELECT id, operator, phone_number, price_mmk FROM beautiful_numbers WHERE id = ?", (b_num_id,), fetchone=True)

async def admin_get_all_orders():
    return await _db_query("SELECT order_id, user_id, package_name, credit_cost, status, created_at FROM orders ORDER BY created_at DESC", fetchall=True)

async def admin_get_all_user_ids():
    return await _db_query("SELECT user_id FROM users WHERE is_banned = 0", fetchall=True)

async def admin_set_ban_status(user_id: int, is_banned: bool):
    return await _db_query("UPDATE users SET is_banned = ? WHERE user_id = ?", (int(is_banned), user_id), commit=True)

async def admin_adjust_user_credits(user_id: int, amount: float):
    return await _db_query("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id), commit=True)

async def admin_purge_user(user_id: int):
    await _db_query("DELETE FROM orders WHERE user_id = ?", (user_id,), commit=True)
    await _db_query("DELETE FROM users WHERE user_id = ?", (user_id,), commit=True)
    return True

async def admin_update_product_name(product_id: str, new_name: str):
    return await _db_query("UPDATE products SET name = ? WHERE product_id = ?", (new_name, product_id), commit=True)

async def admin_update_product_category(product_id: str, new_category: str):
    return await _db_query("UPDATE products SET category = ? WHERE product_id = ?", (new_category, product_id), commit=True)

async def admin_update_product_price(product_id: str, new_price_mmk: int):
    return await _db_query("UPDATE products SET price_mmk = ? WHERE product_id = ?", (new_price_mmk, product_id), commit=True)

async def admin_get_all_products():
    return await _db_query("SELECT operator, category, name, product_id, price_mmk, is_active FROM products ORDER BY operator, category, name", fetchall=True)

async def admin_add_product(product_id: str, operator: str, category: str, name: str, price_mmk: int, extra_info: str = None):
    return await _db_query("INSERT INTO products (product_id, operator, category, name, price_mmk, extra_info) VALUES (?, ?, ?, ?, ?, ?)", (product_id, operator, category, name, price_mmk, extra_info), commit=True)

async def admin_delete_product(product_id: str):
    return await _db_query("DELETE FROM products WHERE product_id = ?", (product_id,), commit=True)

async def admin_add_beautiful_number(operator: str, phone_number: str, price_mmk: int):
    return await _db_query("INSERT INTO beautiful_numbers (operator, phone_number, price_mmk) VALUES (?, ?, ?)", (operator, phone_number, price_mmk), commit=True)