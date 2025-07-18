# handlers.py
import html
from datetime import datetime, timedelta
import random
import string
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest

import database as db
import keyboards
import config
import locale
import middleware
from products import calculate_credit_cost
from config import logger

# States
(
    SELECTING_CREDIT_OPTION, AWAITING_MANUAL_AMOUNT, SELECTING_PAYMENT, AWAITING_SCREENSHOT,
    SHOP_OPERATOR, SHOP_CATEGORY, SHOP_PRODUCT_LIST, SHOP_CONFIRM, AWAITING_PHONE_NUMBER,
    VIEWING_ORDERS
) = range(10)

def generate_order_id(prefix="ORD"):
    return f"{prefix}-{datetime.now().strftime('%y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"

async def answer_query_safely(query: Update.callback_query):
    if not query: return
    try: await query.answer()
    except BadRequest: pass

async def get_lang(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> str:
    if 'lang' in context.user_data: return context.user_data['lang']
    user_db_data = await db.get_user_data(user_id)
    lang = user_db_data.get('language', 'en')
    context.user_data['lang'] = lang
    return lang

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await middleware.force_join_middleware(update, context): return ConversationHandler.END
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"🚀 User {user.id} ({user.full_name}) executed /start or join check.")
    user_data = await db.get_user_data(user.id)
    lang = user_data.get('language', 'en')
    text = locale.get_text('welcome', lang, name=html.escape(user.full_name), user_id=user.id, credits=user_data['credits'])
    if update.callback_query: await update.callback_query.message.delete()
    await context.bot.send_message(
        chat_id=chat_id, text=text, 
        reply_markup=keyboards.get_main_menu_keyboard(lang), 
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if not await middleware.force_join_middleware(update, context): return ConversationHandler.END
    await answer_query_safely(query)
    user = query.from_user
    logger.info(f"🔄 User {user.id} returned to main menu via button '{query.data}'.")
    user_data = await db.get_user_data(user.id)
    lang = user_data.get('language', 'en')
    text = locale.get_text('welcome', lang, name=html.escape(user.full_name), user_id=user.id, credits=user_data['credits'])
    try:
        await query.edit_message_text(text=text, reply_markup=keyboards.get_main_menu_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
    except BadRequest as e:
        if "message is not modified" not in str(e).lower(): await start(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await middleware.force_join_middleware(update, context): return
    query = update.callback_query
    user_id = query.from_user.id
    if 'lang' in context.user_data: del context.user_data['lang']
    current_lang = await get_lang(context, user_id)
    new_lang = 'my' if current_lang == 'en' else 'en'
    await db.set_user_language(user_id, new_lang)
    context.user_data['lang'] = new_lang
    logger.info(f"🌐 User {user_id} changed language to '{new_lang}'.")
    await show_main_menu(update, context)

async def universal_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.effective_user.id
    logger.warning(f"❌ User {user_id} cancelled an operation.")
    lang = await get_lang(context, user_id)
    if update.callback_query:
        await answer_query_safely(update.callback_query)
        await show_main_menu(update, context)
    else:
        await update.message.reply_text(locale.get_text('operation_cancelled', lang))
        await start(update, context)
    context.user_data.clear()
    return ConversationHandler.END

async def credits_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await middleware.force_join_middleware(update, context): return ConversationHandler.END
    query = update.callback_query
    logger.info(f"💰 User {query.from_user.id} started credit purchase flow.")
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    await query.edit_message_text(text=locale.get_text('buy_credits_prompt', lang), reply_markup=keyboards.get_credit_packages_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
    return SELECTING_CREDIT_OPTION

async def credits_package_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    price = int(query.data.split('_')[2])
    context.user_data['price_mmk'] = price
    text = locale.get_text('package_choice_prompt', lang, price=price)
    await query.edit_message_text(text=text, reply_markup=keyboards.get_payment_method_keyboard(price, lang), parse_mode=ParseMode.MARKDOWN)
    return SELECTING_PAYMENT

async def credits_manual_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    await query.edit_message_text(locale.get_text('ask_manual_amount', lang), parse_mode=ParseMode.MARKDOWN)
    return AWAITING_MANUAL_AMOUNT

async def credits_manual_amount_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = await get_lang(context, update.effective_user.id)
    try:
        price = int(update.message.text)
        if price < 500: await update.message.reply_text(locale.get_text('min_amount_prompt', lang)); return AWAITING_MANUAL_AMOUNT
        context.user_data['price_mmk'] = price
        text = locale.get_text('manual_choice_prompt', lang, price=price)
        await update.message.reply_text(text=text, reply_markup=keyboards.get_payment_method_keyboard(price, lang), parse_mode=ParseMode.MARKDOWN)
        return SELECTING_PAYMENT
    except ValueError: await update.message.reply_text(locale.get_text('invalid_amount_prompt', lang)); return AWAITING_MANUAL_AMOUNT

async def credits_payment_method_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    _, method, price_str = query.data.split('_')
    price = int(price_str)
    credit_amount = calculate_credit_cost(price)
    logger.info(f"💳 User {query.from_user.id} is paying {price} MMK for {credit_amount} credits via {method}.")
    payment_method = "Wave Money" if method == 'wave' else "KBZ Pay"
    payment_number = config.WAVE_PAY_NUMBER if method == 'wave' else config.KBZ_PAY_NUMBER
    order_id = generate_order_id("CRD")
    context.user_data.update({'order_id': order_id, 'credit_amount': credit_amount})
    await db.create_order(
        order_id=order_id, user_id=query.from_user.id, order_type='credit_purchase',
        package_name=f"{credit_amount:.2f} Credits", credit_cost=credit_amount,
        payment_method=payment_method, status='pending_payment')
    text = locale.get_text('payment_instructions', lang, order_id=order_id, price=price, credits=credit_amount, number=payment_number, method=payment_method)
    await query.edit_message_text(text, reply_markup=keyboards.get_cancel_flow_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
    return AWAITING_SCREENSHOT

async def credits_screenshot_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ud = context.user_data
    lang = await get_lang(context, user.id) 
    if not ud.get('order_id'):
        await update.message.reply_text(locale.get_text('session_expired', lang)); await start(update, context); return ConversationHandler.END
    order_id = ud['order_id']
    logger.info(f"📸 User {user.id} submitted a screenshot for credit order {order_id}.")
    photo_id = update.message.photo[-1].file_id
    await db.update_order_status_and_screenshot(order_id, 'pending_approval', photo_id)
    await update.message.reply_text(locale.get_text('payment_submitted', lang))
    user_username = f"(@{user.username})" if user.username else ""
    admin_caption = (f"🚨 <b>New Credit Payment</b> 🚨\n\n"
                     f"User: {html.escape(user.full_name)} {user_username}\n"
                     f"ID: <code>{user.id}</code>\n"
                     f"Order ID: <code>{order_id}</code>\n"
                     f"Amount: <b>{ud.get('credit_amount', 'N/A'):.2f} Credits</b>")
    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data=f"admin_approve_credit_{order_id}_{user.id}"),
         InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_credit_{order_id}_{user.id}")]])
    try:
        await context.bot.send_photo(config.CREDIT_REVIEW_CHANNEL, photo_id, caption=admin_caption, reply_markup=admin_keyboard, parse_mode=ParseMode.HTML)
    except Exception as e:
        config.logger.error(f"Failed to send to CREDIT_REVIEW_CHANNEL: {e}")
        await context.bot.send_photo(next(iter(config.ADMIN_IDS)), photo_id, caption="[FALLBACK] " + admin_caption, reply_markup=admin_keyboard, parse_mode=ParseMode.HTML)
    context.user_data.clear()
    await start(update, context)
    return ConversationHandler.END

async def get_products_from_cache(context: ContextTypes.DEFAULT_TYPE, operator: str, category: str) -> list:
    cache = context.bot_data.setdefault('global_product_cache', {})
    cache_key = f"{operator}_{category}"
    if cache_key in cache:
        data, timestamp = cache[cache_key]
        if datetime.now() - timestamp < timedelta(seconds=60):
            logger.info(f"CACHE HIT for {cache_key}")
            return data
    logger.info(f"CACHE MISS for {cache_key}. Fetching from database.")
    if category == "Beautiful Numbers": new_data = await db.get_beautiful_numbers(operator)
    else: new_data = await db.get_products_in_category(operator, category)
    cache[cache_key] = (new_data, datetime.now())
    context.bot_data['global_product_cache'] = cache
    return new_data

async def shop_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await middleware.force_join_middleware(update, context): return ConversationHandler.END
    query = update.callback_query
    logger.info(f"🛍️ User {query.from_user.id} started browsing products.")
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    await query.edit_message_text(locale.get_text('select_operator', lang), reply_markup=await keyboards.get_operator_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
    return SHOP_OPERATOR

async def shop_operator_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    operator = query.data.split('_')[2]
    context.user_data['operator'] = operator
    text = locale.get_text('select_category', lang, operator=operator)
    await query.edit_message_text(text, reply_markup=await keyboards.get_category_keyboard(operator, lang), parse_mode=ParseMode.MARKDOWN)
    return SHOP_CATEGORY

async def shop_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    parts = query.data.split('_')
    operator = parts[2]
    page = int(parts[-1])
    category = " ".join(parts[3:-1]).replace("_", " ")
    logger.info(f"📂 User {query.from_user.id} viewing products for {operator} -> {category} (Page {page}).")
    context.user_data.update({'operator': operator, 'category': category})
    product_list = await get_products_from_cache(context, operator, category)
    if category == "Beautiful Numbers":
        text = locale.get_text('beautiful_numbers_title', lang, operator=operator)
        markup = await keyboards.get_beautiful_numbers_keyboard(product_list, operator, lang, page)
    else:
        text = locale.get_text('select_product', lang, operator=operator, category=category)
        markup = await keyboards.get_product_keyboard(product_list, operator, category, lang, page)
    await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    return SHOP_PRODUCT_LIST

async def shop_cancel_to_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await answer_query_safely(query)
    lang = await get_lang(context, query.from_user.id)
    operator = context.user_data.get('operator')
    if not operator: return await shop_start(update, context)
    text = locale.get_text('select_category', lang, operator=operator)
    await query.edit_message_text(text, reply_markup=await keyboards.get_category_keyboard(operator, lang), parse_mode=ParseMode.MARKDOWN)
    return SHOP_CATEGORY

async def shop_product_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = await get_lang(context, query.from_user.id)
    await answer_query_safely(query)
    product_type, product_id_str = query.data.split('_', 2)[1:]
    is_bnum = (product_type == 'bnum')
    if is_bnum:
        product_id = int(product_id_str)
        product_details = await db.get_beautiful_number_by_id(product_id)
        if not product_details: await query.answer("Sorry, this number is no longer available.", show_alert=True); return SHOP_PRODUCT_LIST
        _, operator, name, price_mmk = product_details
    else:
        product_id = product_id_str
        product_details = await db.get_product_by_id(product_id)
        if not product_details: await query.answer("Sorry, this product is no longer available.", show_alert=True); return SHOP_PRODUCT_LIST
        _, operator, _, name, price_mmk, _ = product_details
    credit_cost = calculate_credit_cost(price_mmk)
    context.user_data['product_selection'] = {'id': product_id, 'name': name, 'cost': credit_cost, 'is_bnum': is_bnum, 'operator': operator}
    text = locale.get_text('confirm_purchase_title', lang, name=name, operator=operator, cost=credit_cost)
    await query.edit_message_text(text, reply_markup=keyboards.get_product_confirmation_keyboard(product_id_str, is_bnum, lang), parse_mode=ParseMode.MARKDOWN)
    return SHOP_CONFIRM

async def shop_beautiful_number_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await answer_query_safely(query)
    lang = await get_lang(context, query.from_user.id)
    operator = context.user_data.get('operator')
    if not operator: return
    instructions_text = locale.get_text('bnum_instructions_text', lang)
    back_cb = f"shop_cat_{operator}_Beautiful_Numbers_1"
    await query.edit_message_text(
        text=instructions_text, parse_mode=None,
        reply_markup=InlineKeyboardMarkup([[keyboards.back_button(back_cb, lang)]])
    )
    return SHOP_PRODUCT_LIST

async def shop_confirm_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await answer_query_safely(query)
    user = query.from_user
    lang = await get_lang(context, user.id)
    selection = context.user_data.get('product_selection')
    if not selection:
        await query.answer(locale.get_text('session_expired', lang), show_alert=True); await show_main_menu(update, context); return ConversationHandler.END
    logger.info(f"🛒 User {user.id} is attempting to purchase '{selection['name']}' for {selection['cost']} credits.")
    user_data = await db.get_user_data(user.id)
    if user_data['credits'] < selection['cost']:
        await query.answer(locale.get_text('insufficient_credits', lang), show_alert=True)
        text = locale.get_text('credit_low_prompt', lang, needed=selection['cost'], has=user_data['credits'])
        await query.edit_message_text(text, reply_markup=keyboards.get_main_menu_keyboard(lang), parse_mode=ParseMode.MARKDOWN)
        return ConversationHandler.END
    if selection['is_bnum']:
        delivery_info = locale.get_text('delivery_bnum', lang)
        return await finalize_order(update, context, delivery_info=delivery_info)
    else:
        text = locale.get_text('ask_phone_number', lang, name=selection['name'], cost=selection['cost'])
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN)
        return AWAITING_PHONE_NUMBER

async def shop_phone_number_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone_number = update.message.text
    if not phone_number.isdigit() or len(phone_number) < 7:
        lang = await get_lang(context, update.effective_user.id)
        await update.message.reply_text(locale.get_text('invalid_amount_prompt', lang))
        return AWAITING_PHONE_NUMBER
    return await finalize_order(update, context, delivery_info=phone_number)

async def finalize_order(update: Update, context: ContextTypes.DEFAULT_TYPE, delivery_info: str):
    user = update.effective_user
    lang = await get_lang(context, user.id)
    selection = context.user_data.get('product_selection')
    if not selection:
        await context.bot.send_message(user.id, locale.get_text('session_expired', lang)); await start(update, context); return ConversationHandler.END
    order_id = generate_order_id("PROD")
    logger.info(f"✅ User {user.id} finalized order {order_id} for '{selection['name']}'. Credits deducted: {selection['cost']}.")
    await db.change_user_credits(user.id, -selection['cost'])
    await db.create_order(
        order_id=order_id, user_id=user.id, order_type='product_purchase',
        package_name=selection['name'], credit_cost=selection['cost'],
        status='pending_approval', delivery_info=delivery_info)
    delivery_text = locale.get_text('delivery_to_phone', lang, phone=delivery_info) if not selection['is_bnum'] else delivery_info
    user_msg_text = locale.get_text('order_submitted', lang, order_id=order_id, name=selection['name'], cost=selection['cost'], delivery_info=delivery_text)
    if update.callback_query: await update.callback_query.edit_message_text(user_msg_text, parse_mode=ParseMode.MARKDOWN)
    else: await update.message.reply_text(user_msg_text, parse_mode=ParseMode.MARKDOWN)
    await start(update, context)
    user_username = f"(@{user.username})" if user.username else ""
    admin_caption = (f"📦 <b>New Product Order</b> 📦\n\n"
                     f"User: {html.escape(user.full_name)} {user_username}\n"
                     f"ID: <code>{user.id}</code>\n"
                     f"Order ID: <code>{order_id}</code>\n\n"
                     f"Deliver: <code>{html.escape(selection['name'])}</code>\n"
                     f"To: <code>{html.escape(delivery_info)}</code>\n"
                     f"Operator: <b>{html.escape(selection['operator'])}</b>")
    admin_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Done", callback_data=f"admin_approve_product_{order_id}_{user.id}"),
        InlineKeyboardButton("❌ Reject (Refund)", callback_data=f"admin_reject_product_{order_id}_{user.id}")
    ]])
    try:
        await context.bot.send_message(config.ORDER_FULFILLMENT_CHANNEL, admin_caption, reply_markup=admin_keyboard, parse_mode=ParseMode.HTML)
    except Exception as e:
        config.logger.error(f"Failed to send to ORDER_FULFILLMENT_CHANNEL: {e}")
        await context.bot.send_message(next(iter(config.ADMIN_IDS)), "[FALLBACK] " + admin_caption, reply_markup=admin_keyboard, parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def my_orders_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await middleware.force_join_middleware(update, context): return ConversationHandler.END
    query = update.callback_query
    user = query.from_user
    logger.info(f"📋 User {user.id} is viewing their orders.")
    lang = await get_lang(context, user.id)
    await answer_query_safely(query)
    page = 1
    if len(query.data.split('_')) > 2:
        try: page = int(query.data.split('_')[-1])
        except (ValueError, IndexError): page = 1
    if 'my_orders_cache' not in context.user_data:
        pending, history = await db.get_user_orders(query.from_user.id)
        context.user_data['my_orders_cache'] = pending + history
    all_orders = context.user_data['my_orders_cache']
    paginated_orders, total_pages, current_page = keyboards.paginate(all_orders, page, page_size=5)
    text = locale.get_text('my_orders_title', lang)
    if paginated_orders:
        for o_id, pkg, status, ts_str, cost in paginated_orders:
            emoji = '⏳'
            if status == 'completed': emoji = '✅'
            elif status == 'rejected': emoji = '❌'
            date_obj = datetime.fromisoformat(ts_str)
            date_formatted = date_obj.strftime('%b %d, %H:%M')
            text += emoji + " " + locale.get_text('order_line', lang, order_id=o_id, pkg=pkg, status=status.replace("_", " ").title(), cost=cost, date=date_formatted)
    else:
        text += locale.get_text('no_orders', lang)
    markup = keyboards.get_my_orders_keyboard(paginated_orders, total_pages, current_page, lang)
    await query.edit_message_text(text, reply_markup=markup, parse_mode=ParseMode.MARKDOWN)
    return VIEWING_ORDERS

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"🚨 Exception while handling an update: {context.error}", exc_info=context.error)