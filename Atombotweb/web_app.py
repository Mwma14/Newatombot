from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import asyncio
import telegram
import html
from datetime import datetime
import random
import string

import database as db
from products import calculate_credit_cost
import config
from config import logger

app = Flask(__name__)
app.secret_key = 'a-much-more-secure-secret-key-for-production'

@app.context_processor
def inject_config():
    return dict(config=config)

async def send_telegram_notification(message, keyboard, order_type):
    bot = telegram.Bot(token=config.TOKEN)
    try:
        if "CREDIT" in order_type.upper():
            target_channel = config.CREDIT_REVIEW_CHANNEL
        else:
            target_channel = config.ORDER_FULFILLMENT_CHANNEL

        await bot.send_message(
            chat_id=target_channel, 
            text=message, 
            reply_markup=keyboard, 
            parse_mode=telegram.constants.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Failed to send notification to {target_channel}: {e}")
        first_admin_id = next(iter(config.ADMIN_IDS))
        await bot.send_message(
            chat_id=first_admin_id,
            text="[FALLBACK] " + message,
            reply_markup=keyboard,
            parse_mode=telegram.constants.ParseMode.HTML
        )

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
async def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id or not user_id.isdigit():
            flash('Please enter a valid numeric User ID', 'danger')
            return redirect(url_for('login'))
        try:
            user_id = int(user_id)
            await db.get_user_data(user_id)
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Login error for user {user_id}: {e}")
            flash('Login failed. Please check your User ID and try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
async def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_id = session['user_id']
    user_data = await db.get_user_data(user_id)
    pending, history = await db.get_user_orders(user_id)
    recent_orders = (pending + history)[:5]
    
    formatted_recent_orders = [{
        'id': o[0], 'package': o[1], 'status': o[2].replace('_', ' ').title(), 
        'cost': o[4], 'date': datetime.fromisoformat(o[3]).strftime('%b %d, %Y')
    } for o in recent_orders]
    
    return render_template('dashboard.html', user_data=user_data, user_id=user_id, recent_orders=formatted_recent_orders)

@app.route('/shop')
async def shop():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('shop.html')

@app.route('/api/shop-data')
async def api_shop_data():
    if 'user_id' not in session: return jsonify({"error": "Unauthorized"}), 401
    all_products = await db.admin_get_all_products()
    organized_products = {}
    for op, cat, name, prod_id, price, active in all_products:
        if not active: continue
        if op not in organized_products: organized_products[op] = {}
        if cat not in organized_products[op]: organized_products[op][cat] = []
        organized_products[op][cat].append({
            'id': prod_id, 'name': name, 'price': price,
            'credits': calculate_credit_cost(price), 'type': 'product'
        })
    return jsonify(organized_products)

@app.route('/shop/<operator>/<category>')
async def shop_category(operator, category):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    category_name = category.replace('_', ' ')
    products_with_credits = []
    if category_name == "Beautiful Numbers":
        products = await db.get_beautiful_numbers(operator)
        for prod_id, phone, price in products:
            products_with_credits.append({
                'id': prod_id, 'name': phone, 'price': price, 'extra': '',
                'credits': calculate_credit_cost(price), 'type': 'bnum'
            })
    else:
        products = await db.get_products_in_category(operator, category_name)
        for prod_id, name, price, extra in products:
            products_with_credits.append({
                'id': prod_id, 'name': name, 'price': price, 'extra': extra or '',
                'credits': calculate_credit_cost(price), 'type': 'product'
            })
            
    return render_template('shop_category.html', 
                         operator=operator, category=category_name, products=products_with_credits)

@app.route('/purchase_credits', methods=['POST'])
async def purchase_credits():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = await request.get_json()
    price = data.get('price')
    user_id = session['user_id']
    if not isinstance(price, int) or price < 500:
        return jsonify({'success': False, 'error': 'Invalid amount. Minimum is 500 MMK.'})

    credit_amount = calculate_credit_cost(price)
    order_id = f"CRD-WEB-{datetime.now().strftime('%y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

    await db.create_order(
        order_id=order_id, user_id=user_id, order_type='credit_purchase',
        package_name=f"{credit_amount:.2f} Credits Request", credit_cost=credit_amount,
        payment_method="Web Request", status='pending_payment')

    admin_caption = (f"🚨 <b>[WEB CREDIT REQUEST]</b> 🚨\n\n"
                     f"User ID: <code>{user_id}</code> has requested to buy credits.\n"
                     f"Order ID: <code>{order_id}</code>\n"
                     f"Amount: <b>{price:,} MMK</b> ({credit_amount:.2f} Credits)\n\n"
                     f"Tell the user to contact you with the Order ID after they have paid. Approve this order only after confirming payment.")
    admin_keyboard = telegram.InlineKeyboardMarkup([[
        telegram.InlineKeyboardButton("✅ Approve Credits", callback_data=f"admin_approve_credit_{order_id}_{user_id}"),
        telegram.InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_credit_{order_id}_{user_id}")]])

    await send_telegram_notification(admin_caption, admin_keyboard, 'credit_purchase')
    return jsonify({'success': True, 'message': f'Your request for {credit_amount:.2f} credits has been logged with Order ID: {order_id}. Please make the payment and contact an admin with this Order ID to get your credits approved.'})

@app.route('/purchase', methods=['POST'])
async def purchase():
    if 'user_id' not in session: return jsonify({'success': False, 'error': 'Not logged in'}), 401
    data = await request.get_json()
    user_id = session['user_id']
    product_id = data.get('product_id')
    product_type = data.get('product_type')
    phone_number = data.get('phone_number', '')

    try:
        user_data = await db.get_user_data(user_id)
        if product_type == 'bnum':
            product_details = await db.get_beautiful_number_by_id(int(product_id))
            if not product_details: return jsonify({'success': False, 'error': 'This number is no longer available.'})
            _, operator, name, price_mmk = product_details
            delivery_info = "Beautiful Number delivery (Contact User)"
        else:
            product_details = await db.get_product_by_id(product_id)
            if not product_details: return jsonify({'success': False, 'error': 'This product is no longer available.'})
            if not phone_number or not phone_number.isdigit(): return jsonify({'success': False, 'error': 'A valid phone number is required.'})
            _, operator, _, name, price_mmk, _ = product_details
            delivery_info = phone_number

        credit_cost = calculate_credit_cost(price_mmk)
        if user_data['credits'] < credit_cost:
            return jsonify({'success': False, 'error': f"Insufficient credits. You need {credit_cost:.2f} C, but you only have {user_data['credits']:.2f} C."})

        order_id = f"WEB-{datetime.now().strftime('%y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        await db.change_user_credits(user_id, -credit_cost)
        await db.create_order(
            order_id=order_id, user_id=user_id, order_type='product_purchase',
            package_name=name, credit_cost=credit_cost, status='pending_approval', delivery_info=delivery_info)

        admin_caption = (f"📦 <b>[WEB ORDER]</b> 📦\n\n"
                         f"User ID: <code>{user_id}</code>\n"
                         f"Order ID: <code>{order_id}</code>\n\n"
                         f"Deliver: <code>{html.escape(name)}</code>\n"
                         f"To: <code>{html.escape(delivery_info)}</code>\n"
                         f"Operator: <b>{html.escape(operator)}</b>")
        admin_keyboard = telegram.InlineKeyboardMarkup([[
            telegram.InlineKeyboardButton("✅ Done", callback_data=f"admin_approve_product_{order_id}_{user_id}"),
            telegram.InlineKeyboardButton("❌ Reject (Refund)", callback_data=f"admin_reject_product_{order_id}_{user_id}")]])
        
        await send_telegram_notification(admin_caption, admin_keyboard, 'product_purchase')
        new_balance = user_data["credits"] - credit_cost
        return jsonify({'success': True, 'message': f'Order placed successfully! Order ID: {order_id}. Your new balance is {new_balance:.2f} C.'})
    except Exception as e:
        logger.error(f"Web purchase error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': 'An unexpected server error occurred.'}), 500

@app.route('/credits')
async def credits():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_data = await db.get_user_data(session['user_id'])
    payment_methods = [{'name': 'KBZ Pay', 'number': config.KBZ_PAY_NUMBER}, {'name': 'Wave Pay', 'number': config.WAVE_PAY_NUMBER}]
    return render_template('credits.html', packages=config.CREDIT_PACKAGES, payment_methods=payment_methods, user_data=user_data)

@app.route('/orders')
async def orders():
    if 'user_id' not in session: return redirect(url_for('login'))
    user_id = session['user_id']
    pending, history = await db.get_user_orders(user_id)
    
    async def format_order_list(orders):
        formatted = []
        for o_id, pkg, status, ts_str, cost in orders:
            order_details = await db.get_order_details(o_id)
            o_type = order_details[4] if order_details else 'Unknown'
            formatted.append({
                'id': o_id, 'package': pkg, 'status': status.replace('_', ' ').title(), 'cost': cost,
                'date': datetime.fromisoformat(ts_str).strftime('%b %d, %Y %H:%M'),
                'type': 'Credit Purchase' if o_type == 'credit_purchase' else 'Product Purchase'
            })
        return formatted
    
    user_data = await db.get_user_data(user_id)
    return render_template('orders.html', pending_orders=await format_order_list(pending), completed_orders=await format_order_list(history), user_data=user_data)

@app.route('/admin')
def admin():
    if session.get('user_id') not in config.ADMIN_IDS: return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route('/admin/orders')
async def admin_orders():
    if session.get('user_id') not in config.ADMIN_IDS: return redirect(url_for('dashboard'))
    all_orders = await db.admin_get_all_orders()
    formatted_orders = [{
        'id': o[0], 'user_id': o[1], 'package': o[2], 'cost': o[3], 'status': o[4].replace('_', ' ').title(),
        'timestamp': datetime.fromisoformat(o[5]).strftime('%Y-%m-%d %H:%M')
    } for o in all_orders]
    return render_template('admin_orders.html', orders=formatted_orders)

@app.route('/admin/users')
async def admin_users():
    if session.get('user_id') not in config.ADMIN_IDS: return redirect(url_for('dashboard'))
    user_ids = await db.admin_get_all_user_ids()
    users = [dict({'id': uid}, **await db.get_user_data(uid)) for (uid,) in user_ids[:50]]
    return render_template('admin_users.html', users=users)

@app.route('/admin/products')
async def admin_products():
    if session.get('user_id') not in config.ADMIN_IDS: return redirect(url_for('dashboard'))
    all_products = await db.admin_get_all_products()
    formatted_products = [{
        'id': p[3], 'operator': p[0], 'category': p[1], 'name': p[2], 'price': p[4], 'active': p[5]
    } for p in all_products]
    return render_template('admin_products.html', products=formatted_products)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))