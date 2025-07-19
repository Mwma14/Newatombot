# middleware.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.error import TelegramError, BadRequest
from config import FORCE_JOIN_CHANNEL, logger
import database as db

async def check_if_banned(user_id: int) -> bool:
    """Helper function to check user's ban status."""
    user_data = await db.get_user_data(user_id)
    return user_data.get('is_banned', False)

async def force_join_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Middleware that checks for ban status first, then channel membership.
    """
    user = update.effective_user
    
    # 1. Check for Ban Status First
    if await check_if_banned(user.id):
        logger.warning(f"🚫 Access Denied: Banned user {user.id} tried to use the bot.")
        return False

    # 2. Check for Admin status or if the feature is disabled
    if not FORCE_JOIN_CHANNEL or user.id in context.bot_data.get("ADMIN_IDS", set()):
        return True

    # 3. Check Channel Membership
    try:
        member = await context.bot.get_chat_member(chat_id=FORCE_JOIN_CHANNEL, user_id=user.id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    except BadRequest as e:
        if "user not found" in e.message.lower():
            # This is expected if the user is not in the channel.
            pass
        else:
            # This could be a permissions issue (bot not admin in channel).
            logger.error(f"BOT PERMISSION ERROR in {FORCE_JOIN_CHANNEL}: {e}. Bot must be an admin. Allowing user to pass.")
            return True
    except TelegramError as e:
        logger.error(f"TelegramError checking membership: {e}. Allowing user to pass.")
        return True
    
    # --- If the check fails, deny access ---
    logger.info(f"User {user.id} denied access: Not a member of {FORCE_JOIN_CHANNEL}.")
    
    join_url = f"https://t.me/{FORCE_JOIN_CHANNEL.lstrip('@')}"
    text = (
        f"👋 **Access Denied | အသုံးပြုခွင့်မရှိပါ**\n\n"
        f"To use this bot, you must first join our channel.\n"
        f"ဤဘော့တ်ကို အသုံးပြုရန်၊ ကျွန်ုပ်တို့၏ချန်နယ်သို့ ဦးစွာဝင်ရောက်ရပါမည်။"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Join Channel | Channel သို့ Join ပါ", url=join_url)],
        [InlineKeyboardButton("✅ I Have Joined | Join ပြီးပါပြီ", callback_data="check_join_status")]
    ])
    
    # --- New, Improved Logic to Prevent Spam ---
    if update.callback_query:
        # If the user specifically clicked the "I Have Joined" button but the check failed
        if update.callback_query.data == 'check_join_status':
            # Just show a pop-up alert and do nothing else. This stops the spam.
            await update.callback_query.answer(
                "You have not joined the channel yet. Please join and then press the button again.",
                show_alert=True
            )
        else:
            # The user clicked a different button (e.g., from the main menu).
            # Edit their current message to show the "Access Denied" screen.
            try:
                await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode='Markdown')
            except BadRequest as e:
                # Ignore "message is not modified" error, but handle others.
                if "message is not modified" not in str(e).lower():
                    await context.bot.send_message(user.id, text, reply_markup=keyboard, parse_mode='Markdown')
    else:
        # This was a command like /start, not a button press. Send a new message.
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode='Markdown')
        
    # Block the original handler from running
    return False