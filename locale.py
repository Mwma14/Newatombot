# translations.py

# This dictionary holds all the text for the bot.
# All special Markdown characters (*, _, etc.) have been removed, except for ``.
TRANSLATIONS = {
    'en': {
        'welcome': "👋 Welcome, {name}!\n\n👤 User ID: `{user_id}`\n💰 Your Credits: {credits:.2f} C\n\n"
                   "Please choose an option from the menu below:",
        'main_menu_button_browse': "🛍️ Browse Products",
        'main_menu_button_buy_credits': "💰 Buy Credits",
        'main_menu_button_orders': "📋 My Orders",
        'main_menu_button_refresh': "🔄 Refresh",
        'main_menu_button_language': "🌐 Language / ဘာသာစကား",
        'back_button': "Back",
        'cancel_button': "❌ Cancel",
        'operation_cancelled': "❌ Operation cancelled.",
        'insufficient_credits': "💳 Insufficient Credits! Please buy credits first.",
        'credits_menu_title': "💰 Buy Credits",
        'credits_manual_button': "✏️ Enter Manually",
        'credits_manual_prompt': "Enter credit amount in MMK (minimum 100 MMK):",
        'credits_invalid_amount': "❌ Invalid amount.",
        'credits_amount_too_small': "❌ Minimum amount is 100 MMK.",
        'credits_payment_method': "💳 Select payment method:",
        'credits_payment_kbz': "💙 KBZ Pay",
        'credits_payment_wave': "💜 Wave Pay",
        'credits_payment_back': "🔙 Back",
        'credits_payment_instructions': """
💳 **Payment Instructions**

**Credit:** {credits:.2f} C ({price:,} MMK)
**Method:** {method}
**Account:** `{account}`

**How to:**
1. Send {price:,} MMK to the account above
2. Send payment screenshot
3. Credits will be added automatically

📸 Send the screenshot now:
""",
        'credits_screenshot_received': "📸 Screenshot received. Your credit purchase will be reviewed by admins.",
        'shop_title': "🛍️ **Products**\n\nSelect operator:",
        'shop_category_title': "📁 **{operator}** Categories\n\nSelect category:",
        'shop_product_list_title': "📦 **{operator} - {category}**",
        'shop_product_button': "{name} ({credits:.1f} C)",
        'shop_bnum_info_button': "ℹ️ Beautiful Number Guide",
        'shop_confirm_title': "🛒 **Confirmation**",
        'shop_confirm_text': """
**Item:** {name}
**Price:** {credits:.2f} C ({price:,} MMK)
**Your Credits:** {user_credits:.2f} C

Confirm purchase?
""",
        'shop_buy_button': "✅ Buy",
        'shop_phone_prompt': "📱 Enter your phone number:",
        'shop_phone_invalid': "❌ Invalid phone number.",
        'shop_purchase_success': "🎉 **Success!**\n\nOrder ID: `{order_id}`\n{credits:.2f} C has been deducted.\n\nYour order will be processed by admins.",
        'orders_title': "📋 **My Orders**",
        'orders_pending_title': "⏳ **Pending Orders**",
        'orders_history_title': "📜 **Order History**",
        'orders_no_pending': "No pending orders.",
        'orders_no_history': "No order history.",
        'orders_item_format': "`{order_id}`\n📦 {package}\n💰 {cost:.2f} C | {status}\n📅 {timestamp}\n",
        'language_selection': "🌐 **Select Language:**",
        'language_changed': "✅ Language changed to English.",
        'force_join_message': "🔒 Please join the channel to use this bot:\n\n{channel}",
        'force_join_button': "✅ Check",
        'not_member_error': "❌ You are not a member of the channel. Please join and check again.",
        'bnum_instructions_text': """
📱 **Beautiful Number Purchase Guide**

You are buying a special phone number. The process is:

1. Complete the purchase in this bot with your credits
2. Your order will be sent to our admin team
3. Contact our admin directly on Telegram for delivery arrangements
4. Admin account: @CEO_METAVERSE
5. Tell the admin your Order ID (received after purchase) and delivery address. The SIM will be delivered.
"""
    },
    'my': {
        'welcome': "👋 မင်္ဂလာပါ, {name}!\n\n👤 User ID: `{user_id}`\n💰 သင့် Credit: {credits:.2f} C\n\n"
                   "ကျေးဇူးပြု၍ အောက်ပါမီနူးမှ ရွေးချယ်ပါ:",
        'main_menu_button_browse': "🛍️ ပစ္စည်းများ ကြည့်ရန်",
        'main_menu_button_buy_credits': "💰 Credit ဝယ်ယူရန်",
        'main_menu_button_orders': "📋 ကျွန်ုပ်၏ Orders",
        'main_menu_button_refresh': "🔄 ပြန်လည်စတင်ရန်",
        'main_menu_button_language': "🌐 Language / ဘာသာစကား",
        'back_button': "နောက်သို့",
        'cancel_button': "❌ ပယ်ဖျက်မည်",
        'operation_cancelled': "❌ လုပ်ဆောင်မှုအား ပယ်ဖျက်လိုက်ပါပြီ။",
        'insufficient_credits': "💳 Credit မလုံလောက်ပါ။ ကျေးဇူးပြု၍ ဦးစွာ Credit ဝယ်ယူပါ။",
        'credits_menu_title': "💰 Credit ဝယ်ယူမည်",
        'credits_manual_button': "✏️ ကိုယ်တိုင်ရိုက်ထည့်မည်",
        'credits_manual_prompt': "Credit ပမာဏအား MMK ဖြင့် ရိုက်ထည့်ပါ (အနည်းဆုံး 100 MMK):",
        'credits_invalid_amount': "❌ မမှန်ကန်သော ပမာဏဖြစ်ပါသည်။",
        'credits_amount_too_small': "❌ အနည်းဆုံး 100 MMK ဖြစ်ရပါမည်။",
        'credits_payment_method': "💳 ငွေပေးချေမှုနည်းလမ်း ရွေးချယ်ပါ:",
        'credits_payment_kbz': "💙 KBZ Pay",
        'credits_payment_wave': "💜 Wave Pay",
        'credits_payment_back': "🔙 နောက်သို့",
        'credits_payment_instructions': """
💳 **ငွေပေးချေမှု လမ်းညွှန်**

**Credit:** {credits:.2f} C ({price:,} MMK)
**နည်းလမ်း:** {method}
**အကောင့်:** `{account}`

**လုပ်ဆောင်ပုံ:**
1. အထက်ပါ အကောင့်သို့ {price:,} MMK ပို့ပါ
2. ငွေပေးချေမှု screenshot အား ပေးပို့ပါ
3. သင့်အား Credit များ အလိုအလျောက် ထည့်သွင်းပေးပါမည်

📸 ယခု screenshot ပေးပို့ပါ:
""",
        'credits_screenshot_received': "📸 Screenshot ရရှိပါပြီ။ သင့် Credit ဝယ်ယူမှုအား Admin များမှ စစ်ဆေးပေးပါမည်။",
        'shop_title': "🛍️ **ပစ္စည်းများ**\n\nOperator ရွေးချယ်ပါ:",
        'shop_category_title': "📁 **{operator}** Categories\n\nCategory ရွေးချယ်ပါ:",
        'shop_product_list_title': "📦 **{operator} - {category}**",
        'shop_product_button': "{name} ({credits:.1f} C)",
        'shop_bnum_info_button': "ℹ️ Beautiful Number Guide",
        'shop_confirm_title': "🛒 **အတည်ပြုခြင်း**",
        'shop_confirm_text': """
**ပစ္စည်း:** {name}
**စျေးနှုန်း:** {credits:.2f} C ({price:,} MMK)
**သင့် Credits:** {user_credits:.2f} C

ဝယ်ယူလိုပါသလား?
""",
        'shop_buy_button': "✅ ဝယ်မည်",
        'shop_phone_prompt': "📱 သင့် ဖုန်းနံပါတ်ကို ရိုက်ထည့်ပါ:",
        'shop_phone_invalid': "❌ မမှန်ကန်သော ဖုန်းနံပါတ်ဖြစ်ပါသည်။",
        'shop_purchase_success': "🎉 **အောင်မြင်ပါပြီ!**\n\nOrder ID: `{order_id}`\nသင့်အား {credits:.2f} C နုတ်ယူပါပြီ။\n\nAdmin များမှ သင့် order အား စစ်ဆေးပေးပါမည်။",
        'orders_title': "📋 **ကျွန်ုပ်၏ Orders**",
        'orders_pending_title': "⏳ **စောင့်ဆိုင်းနေသော Orders**",
        'orders_history_title': "📜 **Order မှတ်တမ်း**",
        'orders_no_pending': "စောင့်ဆိုင်းနေသော order မရှိပါ။",
        'orders_no_history': "Order မှတ်တမ်း မရှိပါ။",
        'orders_item_format': "`{order_id}`\n📦 {package}\n💰 {cost:.2f} C | {status}\n📅 {timestamp}\n",
        'language_selection': "🌐 **ဘာသာစကား ရွေးချယ်ပါ:**",
        'language_changed': "✅ ဘာသာစကားအား မြန်မာသို့ ပြောင်းလဲပါပြီ။",
        'force_join_message': "🔒 ဤ bot အား အသုံးပြုရန် ကျေးဇူးပြု၍ channel တွင် ပါဝင်ပါ:\n\n{channel}",
        'force_join_button': "✅ စစ်ဆေးမည်",
        'not_member_error': "❌ သင်သည် channel ၌ မပါဝင်သေးပါ။ ကျေးဇူးပြု၍ ပါဝင်ပြီး ပြန်လည် စစ်ဆေးပါ။",
        'bnum_instructions_text': """
📱 **Beautiful Number ဝယ်ယူမှု လမ်းညွှန်**

သင်သည် အထူး ဖုန်းနံပါတ် တစ်ခု ဝယ်ယူနေပါသည်။ လုပ်ငန်းစဉ်များမှာ:

1. ဤ bot တွင် သင့် credit များဖြင့် ဝယ်ယူမှု ပြီးစီးပါ
2. သင့် order အား admin team သို့ ပို့ပေးပါမည်
3. ပေးပို့မှု အစီအစဉ်အတွက် Telegram ရှိ ကျွန်ုပ်တို့ admin နှင့် တိုက်ရိုက် ဆက်သွယ်ပါ
4. Admin အကောင့်: @CEO_METAVERSE
5. Admin အား သင့် Order ID (ဝယ်ယူပြီးနောက် ရရှိမည်) နှင့် သင့် ပေးပို့လိပ်စာကို ပြောပြပါ။ နံပါတ် SIM ကို delivery service မှတဆင့် ပို့ပေးပါမည်။
"""
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """Get localized text with optional formatting."""
    try:
        text = TRANSLATIONS[lang].get(key, TRANSLATIONS['en'].get(key, f"Missing: {key}"))
        return text.format(**kwargs) if kwargs else text
    except KeyError:
        return f"Missing translation: {key}"

def get_available_languages():
    """Get list of available language codes."""
    return list(TRANSLATIONS.keys())