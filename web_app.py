
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import asyncio
import threading
import time
from datetime import datetime
import database as db
from products import calculate_credit_cost
import config
from config import logger
import html

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Make config available in templates
@app.context_processor
def inject_config():
    return dict(config=config)

# Store active bot context for web requests
web_context = {}

def run_async(coro):
    """Helper function to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        if not user_id:
            return render_template('login.html', error='Please enter your Telegram User ID')
        try:
            user_id = int(user_id)
            user_data = run_async(db.get_user_data(user_id))
            if user_data['credits'] == 0 and not user_data['is_banned']:
                # New user, initialize with default credits
                run_async(db.change_user_credits(user_id, 0))
            session['user_id'] = user_id
            session['user_data'] = user_data
            return redirect(url_for('dashboard'))
        except ValueError:
            return render_template('login.html', error='Please enter a valid numeric User ID')
        except Exception as e:
            logger.error(f"Login error for user {user_id}: {e}")
            return render_template('login.html', error='Login failed. Please check your User ID.')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    user_data = run_async(db.get_user_data(user_id))
    session['user_data'] = user_data
    
    return render_template('dashboard.html', user_data=user_data, user_id=user_id)

@app.route('/shop')
def shop():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    operators = run_async(db.get_operators())
    return render_template('shop.html', operators=operators)

@app.route('/shop/<operator>')
def shop_operator(operator):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    categories = run_async(db.get_categories_for_operator(operator))
    return render_template('shop_operator.html', operator=operator, categories=categories)

@app.route('/shop/<operator>/<category>')
def shop_category(operator, category):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if category == "Beautiful Numbers":
        products = run_async(db.get_beautiful_numbers(operator))
        product_type = 'bnum'
    else:
        products = run_async(db.get_products_in_category(operator, category))
        product_type = 'product'
    
    # Calculate credit costs
    products_with_credits = []
    for product in products:
        if product_type == 'bnum':
            prod_id, phone, price = product
            credits = calculate_credit_cost(price)
            products_with_credits.append({
                'id': prod_id,
                'name': phone,
                'price': price,
                'credits': credits,
                'type': 'bnum'
            })
        else:
            prod_id, name, price, extra = product
            credits = calculate_credit_cost(price)
            products_with_credits.append({
                'id': prod_id,
                'name': name,
                'price': price,
                'credits': credits,
                'extra': extra or '',
                'type': 'product'
            })
    
    return render_template('shop_category.html', 
                         operator=operator, 
                         category=category, 
                         products=products_with_credits)

@app.route('/purchase', methods=['POST'])
def purchase():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})
    
    user_id = session['user_id']
    product_id = request.json.get('product_id')
    product_type = request.json.get('product_type')
    phone_number = request.json.get('phone_number', '')
    
    try:
        user_data = run_async(db.get_user_data(user_id))
        
        if product_type == 'bnum':
            product_details = run_async(db.get_beautiful_number_by_id(int(product_id)))
            if not product_details:
                return jsonify({'success': False, 'error': 'Product not found'})
            _, operator, name, price_mmk = product_details
        else:
            product_details = run_async(db.get_product_by_id(product_id))
            if not product_details:
                return jsonify({'success': False, 'error': 'Product not found'})
            _, operator, _, name, price_mmk, _ = product_details
        
        credit_cost = calculate_credit_cost(price_mmk)
        
        if user_data['credits'] < credit_cost:
            return jsonify({'success': False, 'error': 'Insufficient credits'})
        
        # Generate order ID
        import random
        import string
        order_id = f"WEB-{datetime.now().strftime('%y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        
        # Deduct credits
        run_async(db.change_user_credits(user_id, -credit_cost))
        
        # Create order
        delivery_info = phone_number if phone_number else "Beautiful Number delivery"
        run_async(db.create_order(
            order_id=order_id,
            user_id=user_id,
            order_type='product_purchase',
            package_name=name,
            credit_cost=credit_cost,
            status='pending_approval',
            delivery_info=delivery_info
        ))
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'message': f'Order placed successfully! Order ID: {order_id}'
        })
        
    except Exception as e:
        logger.error(f"Web purchase error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/credits')
def credits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('credits.html', packages=config.CREDIT_PACKAGES)

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    pending, history = run_async(db.get_user_orders(user_id))
    all_orders = pending + history
    
    # Format orders for display
    formatted_orders = []
    for order in all_orders:
        o_id, pkg, status, ts_str, cost = order
        date_obj = datetime.fromisoformat(ts_str)
        formatted_orders.append({
            'id': o_id,
            'package': pkg,
            'status': status.replace('_', ' ').title(),
            'cost': cost,
            'date': date_obj.strftime('%Y-%m-%d %H:%M')
        })
    
    return render_template('orders.html', orders=formatted_orders)

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    if user_id not in config.ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    return render_template('admin.html')

@app.route('/admin/orders')
def admin_orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['user_id'] not in config.ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    all_orders = run_async(db.admin_get_all_orders())
    
    formatted_orders = []
    for order in all_orders:
        o_id, u_id, pkg, cost, status, ts = order
        ts_formatted = datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M')
        formatted_orders.append({
            'id': o_id,
            'user_id': u_id,
            'package': pkg,
            'cost': cost,
            'status': status.replace('_', ' ').title(),
            'timestamp': ts_formatted
        })
    
    return render_template('admin_orders.html', orders=formatted_orders)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['user_id'] not in config.ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    # Get all user IDs and their basic info
    user_ids = run_async(db.admin_get_all_user_ids())
    users = []
    
    for (uid,) in user_ids[:50]:  # Limit to first 50 users for performance
        user_data = run_async(db.get_user_data(uid))
        users.append({
            'id': uid,
            'credits': user_data['credits'],
            'is_banned': user_data['is_banned']
        })
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/products')
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if session['user_id'] not in config.ADMIN_IDS:
        return redirect(url_for('dashboard'))
    
    all_products = run_async(db.admin_get_all_products())
    
    formatted_products = []
    for product in all_products:
        operator, category, name, prod_id, price, active = product
        formatted_products.append({
            'id': prod_id,
            'operator': operator,
            'category': category,
            'name': name,
            'price': price,
            'active': active
        })
    
    return render_template('admin_products.html', products=formatted_products)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
