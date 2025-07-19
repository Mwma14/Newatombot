# admin.py
import html
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden

import database as db
import config
import keyboards
from config import logger

# States
(
    AWAITING_BNUM_DETAILS, AWAITING_NEW_PRODUCT_DETAILS,
    AWAITING_PRODUCT_ID_TO_EDIT, AWAITING_EDIT_CHOICE, AWAITING_NEW_PRODUCT_NAME,
    AWAITING_NEW_PRODUCT_CATEGORY, AWAITING_NEW_PRODUCT_PRICE,
    AWAITING_PRODUCT_ID_TO_DELETE, AWAITING_DELETE_CONFIRMATION,
    AWAITING_USER_ID_INPUT, AWAITING_CREDIT_ADJUSTMENT,
    AWAITING_BROADCAST_MESSAGE_ALL, AWAITING_BROADCAST_MESSAGE_ONE,
    AWAITING_PURGE_CONFIRMATION
) = range(10, 24)

def is_admin(user_id: int) -> bool: return user_id in config.ADMIN_IDS

def clear_product_cache(context: ContextTypes.DEFAULT_TYPE):
    if 'global_product_cache' in context.bot_data:
        del context.bot_data['global_product_cache']
        logger.info("Global product cache has been cleared.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    keyboard = [
        [InlineKeyboardButton("📊 View All User Orders", callback_data="admin_view_orders_1")],
        [InlineKeyboardButton("👤 Manage User", callback_data="admin_manage_user_start")],
        [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast_start")],
        [InlineKeyboardButton("📋 View All Products", callback_data="admin_view_prods_1")],
        [InlineKeyboardButton("➕ Add Product", callback_data="admin_addprod_start")],
        [InlineKeyboardButton("✏️ Edit Product", callback_data="admin_edit_start")],
        [InlineKeyboardButton("🗑️ Delete Product", callback_data="admin_delete_start")],
        [InlineKeyboardButton("✨ Add Beautiful Number", callback_data="admin_addbnum_start")],
    ]
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("👑 Admin Panel 👑", reply_markup=InlineKeyboardMarkup(keyboard))
    else: await update.message.reply_text("👑 Admin Panel 👑", reply_markup=InlineKeyboardMarkup(keyboard))

async def ask_for_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, flow_tag: str):
    query = update.callback_query
    await query.answer()
    context.user_data['admin_flow'] = flow_tag
    await query.edit_message_text(prompt)
    return AWAITING_USER_ID_INPUT

async def received_user_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    flow = context.user_data.get('admin_flow')
    if not flow:
        await update.message.reply_text("Session expired. Please start again from the /admin panel.")
        return ConversationHandler.END
    if flow == 'manage_user':
        return await manage_user_id_received(update, context)
    elif flow == 'broadcast_one':
        return await broadcast_target_received(update, context)
    else:
        await update.message.reply_text("Unknown flow. Please start again."); return ConversationHandler.END

async def manage_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await ask_for_user_id(update, context, "Please send the User ID of the user you want to manage.", "manage_user")

async def manage_user_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: user_id = int(update.message.text)
    except ValueError: await update.message.reply_text("Invalid ID."); return AWAITING_USER_ID_INPUT
    user_data = await db.get_user_data(user_id)
    try: user_chat = await context.bot.get_chat(user_id)
    except: user_chat = None
    if user_chat is None and user_data['credits'] == 0 and not user_data['is_banned']:
        await update.message.reply_text("User not found in database or on Telegram.")
        return ConversationHandler.END
    user_display_name = html.escape(user_chat.full_name or 'N/A') if user_chat else "Unknown (Bot Blocked)"
    text = (f"👤 Managing User: {user_display_name} (`{user_id}`)\n"
            f"💰 Credits: {user_data['credits']:.2f}\n"
            f"🚫 Banned: {'Yes' if user_data['is_banned'] else 'No'}")
    await update.message.reply_text(text, reply_markup=keyboards.get_user_management_keyboard(user_id, user_data['is_banned']), parse_mode=ParseMode.HTML)
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Choose a broadcast option:", reply_markup=keyboards.get_broadcast_keyboard())

async def broadcast_one_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await ask_for_user_id(update, context, "Please send the User ID of the recipient.", "broadcast_one")

async def broadcast_target_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        target_id = int(update.message.text)
        context.user_data['target_user_id'] = target_id
    except ValueError:
        await update.message.reply_text("Invalid ID. Please send a number."); return AWAITING_USER_ID_INPUT
    await update.message.reply_text(f"Recipient set to `{target_id}`. Now, please send the message you want to deliver.", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_BROADCAST_MESSAGE_ONE

async def view_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('_')[-1])
    if 'all_orders_cache' not in context.bot_data:
        context.bot_data['all_orders_cache'] = await db.admin_get_all_orders()
    all_orders = context.bot_data['all_orders_cache']
    if not all_orders:
        await query.edit_message_text("No orders found.", reply_markup=InlineKeyboardMarkup([[keyboards.back_button("admin_panel")]]))
        return
    paginated_orders, total_pages, current_page = keyboards.paginate(all_orders, page, page_size=10)
    message_text = f"📊 **All User Orders (Page {current_page}/{total_pages})** 📊\n\n"
    for o_id, u_id, pkg, cost, status, ts in paginated_orders:
        ts_formatted = datetime.fromisoformat(ts).strftime('%y-%m-%d %H:%M')
        message_text += f"`{o_id}`\n👤`{u_id}` | `{pkg}`\n💰{cost:.2f} C | {status} | _{ts_formatted}_\n\n"
    keyboard_rows = keyboards.get_pagination_controls(current_page, total_pages, "admin_view_orders")
    keyboard_rows.append([keyboards.back_button("admin_panel")])
    await query.edit_message_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard_rows))

async def adjust_user_credits_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[-1])
    context.user_data['mgmt_user_id'] = user_id
    await query.edit_message_text("Send the amount to add or remove (e.g., `50` to add, `-10` to remove).", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_CREDIT_ADJUSTMENT

async def adjust_user_credits_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: amount = float(update.message.text)
    except ValueError: await update.message.reply_text("Invalid amount."); return AWAITING_CREDIT_ADJUSTMENT
    user_id = context.user_data['mgmt_user_id']
    await db.admin_adjust_user_credits(user_id, amount)
    new_data = await db.get_user_data(user_id)
    await update.message.reply_text(f"✅ Success! User {user_id}'s new balance is {new_data['credits']:.2f}.")
    logger.info(f"ADMIN ACTION: User {update.effective_user.id} adjusted credits of user {user_id} by {amount}.")
    context.user_data.clear()
    return ConversationHandler.END

async def ban_unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split('_'); action = parts[2]; user_id = int(parts[3])
    new_ban_status = True if action == "ban" else False
    await db.admin_set_ban_status(user_id, new_ban_status)
    status_text = "banned"
    if new_ban_status and config.FORCE_JOIN_CHANNEL:
        try: await context.bot.ban_chat_member(config.FORCE_JOIN_CHANNEL, user_id)
        except Exception as e: logger.warning(f"Could not ban {user_id} from channel: {e}")
    elif not new_ban_status and config.FORCE_JOIN_CHANNEL:
        status_text = "unbanned"
        try: await context.bot.unban_chat_member(config.FORCE_JOIN_CHANNEL, user_id)
        except Exception as e: logger.warning(f"Could not unban {user_id} from channel: {e}")
    await query.edit_message_text(f"✅ Success! User {user_id} has been {status_text}.")
    logger.info(f"ADMIN ACTION: User {update.effective_user.id} {status_text} user {user_id}.")
    context.user_data.clear()
    return ConversationHandler.END

async def purge_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split('_')[-1])
    context.user_data['mgmt_user_id'] = user_id
    try: user_chat = await context.bot.get_chat(user_id)
    except: user_chat = None
    user_name = html.escape(user_chat.full_name or 'N/A') if user_chat else "Unknown"
    text = (
        f"⚠️ **FINAL WARNING** ⚠️\n\nYou are about to delete ALL data for user {user_name} (`{user_id}`).\n"
        f"This includes their credit balance and order history. This is irreversible.\n\n"
        f"To confirm, please type `DELETE {user_id}`"
    )
    await query.edit_message_text(text, parse_mode=ParseMode.HTML)
    return AWAITING_PURGE_CONFIRMATION

async def purge_user_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data['mgmt_user_id']
    if update.message.text == f"DELETE {user_id}":
        await db.admin_purge_user(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been purged.")
        logger.warning(f"ADMIN ACTION: User {update.effective_user.id} purged all data for user {user_id}.")
    else: await update.message.reply_text("Incorrect confirmation. Purge cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

async def broadcast_all_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Please send the message to broadcast to all non-banned users.")
    return AWAITING_BROADCAST_MESSAGE_ALL

async def broadcast_all_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    await message.reply_text("Broadcasting started...")
    user_ids = await db.admin_get_all_user_ids()
    count, errors = 0, 0
    for (user_id,) in user_ids:
        try:
            await context.bot.copy_message(chat_id=user_id, from_chat_id=message.chat_id, message_id=message.message_id)
            count += 1
            await asyncio.sleep(0.1)
        except (BadRequest, Forbidden): errors += 1
    await message.reply_text(f"✅ Broadcast complete.\nSent to: {count} users\nFailed: {errors} users")
    logger.info(f"ADMIN ACTION: User {update.effective_user.id} broadcasted to {count} users.")
    return ConversationHandler.END

async def broadcast_one_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    target_id = context.user_data['target_user_id']
    try:
        await context.bot.copy_message(chat_id=target_id, from_chat_id=message.chat_id, message_id=message.message_id)
        await message.reply_text(f"✅ Message sent to {target_id}.")
        logger.info(f"ADMIN ACTION: User {update.effective_user.id} sent a message to user {target_id}.")
    except (BadRequest, Forbidden) as e: await message.reply_text(f"❌ Failed to send message: {e}")
    context.user_data.clear()
    return ConversationHandler.END

async def approval_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try: _, action, order_type, order_id, user_id_str = query.data.split('_', 4)
    except (ValueError, IndexError): await query.edit_message_text("⚠️ Error: Malformed admin callback."); return
    user_id = int(user_id_str)
    order_data = await db.get_order_details(order_id)
    if not order_data: return await query.edit_message_text(f"⚠️ Error: Order <code>{order_id}</code> not found.", parse_mode=ParseMode.HTML)
    _, credit_cost, pkg_name, status, o_type = order_data
    if status != 'pending_approval': return await query.edit_message_text(f"⚠️ Action for <code>{order_id}</code> was already processed.", parse_mode=ParseMode.HTML)
    new_status = 'completed' if action == 'approve' else 'rejected'
    await db.set_order_status(order_id, new_status)
    admin_user = query.from_user
    user_notification = ""
    try:
        user_chat = await context.bot.get_chat(user_id)
        user_display_name = user_chat.full_name or "N/A"
        user_username = f"(@{user_chat.username})" if user_chat.username else ""
    except Exception: user_display_name, user_username = "Unknown User", ""
    user_info = f"<code>{user_id}</code> {html.escape(user_display_name)} {user_username}"
    if new_status == 'completed':
        admin_feedback = (f"Order <code>{order_id}</code>\n"
                          f"For: {user_info}\n"
                          f"Item: <code>{html.escape(pkg_name)}</code> ({credit_cost:.2f} C)\n\n"
                          f"✅ <b>Approved</b> by {html.escape(admin_user.full_name)}")
        if o_type == 'credit_purchase':
            await db.change_user_credits(user_id, credit_cost)
            user_notification = f"🎉 Your purchase of {html.escape(pkg_name)} is approved! {credit_cost:.2f} credits have been added."
        else: user_notification = f"🎉 Your order for {html.escape(pkg_name)} has been processed!"
    else:
        admin_feedback = (f"Order <code>{order_id}</code>\n"
                          f"For: {user_info}\n"
                          f"Item: <code>{html.escape(pkg_name)}</code> ({credit_cost:.2f} C)\n\n"
                          f"❌ <b>Rejected</b> by {html.escape(admin_user.full_name)}")
        await db.change_user_credits(user_id, credit_cost)
        user_notification = f"😞 Your order for {html.escape(pkg_name)} was rejected. {credit_cost:.2f} credits refunded."
    edit_target = query.edit_message_caption if query.message.photo else query.edit_message_text
    await edit_target(admin_feedback, reply_markup=None, parse_mode=ParseMode.HTML)
    try: await context.bot.send_message(chat_id=user_id, text=user_notification, parse_mode=ParseMode.HTML)
    except Exception as e: logger.error(f"Failed to notify user {user_id} for order {order_id}: {e}")

async def admin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Admin operation cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

async def view_all_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split('_')[-1])
    all_products = await db.admin_get_all_products()
    if not all_products:
        await query.edit_message_text("No products found.", reply_markup=InlineKeyboardMarkup([[keyboards.back_button("admin_panel")]]))
        return
    paginated_products, total_pages, current_page = keyboards.paginate(all_products, page, page_size=10)
    message_text = f"📦 *All Products (Page {current_page}/{total_pages})* 📦\n"
    current_operator, current_category = "", ""
    for operator, category, name, prod_id, price, active in paginated_products:
        if operator != current_operator: message_text += f"\n--- *{operator}* ---\n"; current_operator = operator; current_category = ""
        if category != current_category: message_text += f"\n📁 _{category}_\n"; current_category = category
        status_emoji = "✅" if active else "❌"
        message_text += f"  {status_emoji} *{name}* (`{prod_id}`)\n"
    keyboard_rows = keyboards.get_pagination_controls(current_page, total_pages, "admin_view_prods")
    keyboard_rows.append([keyboards.back_button("admin_panel")])
    await query.edit_message_text(message_text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(keyboard_rows))

async def add_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Send new product details on separate lines:\n\n`product_id`\n`OPERATOR`\n`Category`\n`Name`\n`PriceInMMK`\n`ExtraInfo (optional)`", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_NEW_PRODUCT_DETAILS

async def add_product_details_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    details = update.message.text.split('\n')
    if len(details) < 5: await update.message.reply_text("Invalid format. Provide at least 5 lines."); return AWAITING_NEW_PRODUCT_DETAILS
    try:
        product_id, operator, category, name, price_mmk_str = [d.strip() for d in details[:5]]
        price_mmk = int(price_mmk_str)
        extra_info = details[5].strip() if len(details) > 5 and details[5].lower() != 'none' else None
        if await db.get_product_by_id(product_id):
            await update.message.reply_text(f"❌ ID `{product_id}` already exists."); return AWAITING_NEW_PRODUCT_DETAILS
        if await db.admin_add_product(product_id, operator.upper(), category, name, price_mmk, extra_info):
            await update.message.reply_text(f"✅ Product `{name}` added.")
            clear_product_cache(context)
        else: await update.message.reply_text("❌ Error adding product.")
    except (ValueError, IndexError): await update.message.reply_text("Invalid format."); return AWAITING_NEW_PRODUCT_DETAILS
    return ConversationHandler.END

async def edit_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Send the `product_id` to edit.", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_PRODUCT_ID_TO_EDIT

async def edit_product_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = update.message.text.strip()
    product_details = await db.get_product_by_id(product_id)
    if not product_details: await update.message.reply_text("Product ID not found."); return AWAITING_PRODUCT_ID_TO_EDIT
    context.user_data['edit_product'] = {'id': product_id}
    text = (f"*Editing:* `{product_id}`\n\n1. Name: *{product_details[3]}*\n2. Category: *{product_details[2]}*\n3. Price: *{product_details[4]:,} MMK*")
    keyboard = [[InlineKeyboardButton("Edit Name", callback_data="edit_prod_name")], [InlineKeyboardButton("Edit Category", callback_data="edit_prod_category")], [InlineKeyboardButton("Edit Price", callback_data="edit_prod_price")], [InlineKeyboardButton("❌ Cancel", callback_data="edit_prod_cancel")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    return AWAITING_EDIT_CHOICE

async def edit_product_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    field_to_edit, prompt_text, next_state = None, None, None

    if choice == "edit_prod_name":
        field_to_edit = "name"
        prompt_text = "Send the new name."
        next_state = AWAITING_NEW_PRODUCT_NAME
    elif choice == "edit_prod_category":
        field_to_edit = "category"
        prompt_text = "Send the new category."
        next_state = AWAITING_NEW_PRODUCT_CATEGORY
    elif choice == "edit_prod_price":
        field_to_edit = "price"
        prompt_text = "Send the new price in MMK."
        next_state = AWAITING_NEW_PRODUCT_PRICE
    elif choice == "edit_prod_cancel":
        await query.edit_message_text("Editing cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
    else:
        return ConversationHandler.END

    # Store the field we are editing in user_data for the next step
    context.user_data['edit_field'] = field_to_edit
    await query.edit_message_text(prompt_text)
    return next_state


async def edit_product_new_value_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_value = update.message.text.strip()
    # Get the field to edit from user_data (the robust way)
    field_to_edit = context.user_data.get('edit_field')
    product = context.user_data.get('edit_product')

    if not product or not field_to_edit:
        await update.message.reply_text("Session expired or an error occurred. Please start again.")
        context.user_data.clear()
        return ConversationHandler.END

    product_id = product['id']

    if field_to_edit == 'name':
        await db.admin_update_product_name(product_id, new_value)
    elif field_to_edit == 'category':
        await db.admin_update_product_category(product_id, new_value)
    elif field_to_edit == 'price':
        try:
            new_price = int(new_value)
            await db.admin_update_product_price(product_id, new_price)
        except ValueError:
            await update.message.reply_text("Invalid price. Please send a number only.")
            # Stay in the same state to allow the user to try again
            return AWAITING_NEW_PRODUCT_PRICE

    await update.message.reply_text(f"✅ Product `{product_id}` updated successfully.")
    
    # This is crucial: clear the cache so the changes are visible immediately
    clear_product_cache(context)
    
    # Clean up and end the conversation
    context.user_data.clear()
    return ConversationHandler.END

async def delete_product_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Send the `product_id` to **permanently delete**.", parse_mode=ParseMode.MARKDOWN)
    return AWAITING_PRODUCT_ID_TO_DELETE

async def delete_product_id_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = update.message.text.strip()
    product_details = await db.get_product_by_id(product_id)
    if not product_details: await update.message.reply_text("Product ID not found."); return AWAITING_PRODUCT_ID_TO_DELETE
    context.user_data['delete_product_id'] = product_id
    text = (f"⚠️ **Confirm Deletion** ⚠️\n\nDelete product:\nName: **{product_details[3]}**\nID: `{product_details[0]}`\n\nThis is irreversible.")
    keyboard = [[InlineKeyboardButton("YES, DELETE IT", callback_data="delete_confirm_yes")], [InlineKeyboardButton("NO, CANCEL", callback_data="delete_confirm_no")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)
    return AWAITING_DELETE_CONFIRMATION

async def delete_product_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "delete_confirm_no": await query.edit_message_text("Deletion cancelled."); context.user_data.clear(); return ConversationHandler.END
    product_id = context.user_data.get('delete_product_id')
    if not product_id: await query.edit_message_text("Session expired."); return ConversationHandler.END
    if await db.admin_delete_product(product_id):
        await query.edit_message_text(f"✅ Product `{product_id}` has been deleted.")
        clear_product_cache(context)
    else: await query.edit_message_text("❌ Error deleting product.")
    context.user_data.clear()
    return ConversationHandler.END

async def add_bnum_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Send Beautiful Number details:\n`OPERATOR,PhoneNumber,PriceInMMK`", parse_mode='Markdown')
    return AWAITING_BNUM_DETAILS

async def add_bnum_details_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        operator, phone, price_str = update.message.text.split(',')
        price = int(price_str.strip())
        operator = operator.strip().upper()
        if await db.admin_add_beautiful_number(operator, phone.strip(), price):
            await update.message.reply_text(f"✅ Added `{phone}` for `{operator}` at `{price:,}` MMK.")
        else: await update.message.reply_text("❌ Failed to add. Number might exist.")
    except Exception as e: await update.message.reply_text(f"Invalid format.\nError: {e}"); return AWAITING_BNUM_DETAILS
    return ConversationHandler.END