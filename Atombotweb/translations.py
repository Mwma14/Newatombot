
# translations.py
# This file contains all text translations for the Telegram bot

TEXTS = {
    'welcome': {
        'en': "Welcome to **Atom Bot** 🎉\n\n**Hi {name}!**\n\nUser ID: `{user_id}`\n💰 Credits: **{credits:.2f}**\n\nChoose an option below:",
        'my': "**Atom Bot** မှ ကြိုဆိုပါတယ် 🎉\n\n**{name} မင်္ဂလာပါ!**\n\nအသုံးပြုသူ ID: `{user_id}`\n💰 ခရက်ဒစ်: **{credits:.2f}**\n\nအောက်ပါရွေးချယ်မှုများမှ တစ်ခုခုကို ရွေးချယ်ပါ:"
    },
    
    'main_menu_button_browse': {
        'en': '🛒 Browse Products',
        'my': '🛒 ထုတ်ကုန်များကြည့်ရှုရန်'
    },
    
    'main_menu_button_buy_credits': {
        'en': '💳 Buy Credits',
        'my': '💳 ခရက်ဒစ်ဝယ်ယူရန်'
    },
    
    'main_menu_button_orders': {
        'en': '📋 My Orders',
        'my': '📋 ကျွန်ုပ်၏အမှာများ'
    },
    
    'main_menu_button_refresh': {
        'en': '🔄 Refresh',
        'my': '🔄 ပြန်လည်တင်ရန်'
    },
    
    'main_menu_button_language': {
        'en': '🌐 မြန်မာ',
        'my': '🌐 English'
    },
    
    'back_button': {
        'en': 'Back',
        'my': 'နောက်သို့'
    },
    
    'cancel_button': {
        'en': '❌ Cancel',
        'my': '❌ ပယ်ဖျက်ရန်'
    },
    
    'proceed_prompt': {
        'en': 'Proceed',
        'my': 'ဆက်လက်လုပ်ဆောင်ရန်'
    },
    
    'buy_credits_prompt': {
        'en': '💳 **Buy Credits** 💳\n\nSelect a credit package or enter a custom amount:',
        'my': '💳 **ခရက်ဒစ်ဝယ်ယူရန်** 💳\n\nခရက်ဒစ်အစုံတစ်ခုကို ရွေးချယ်ပါ သို့မဟုတ် စိတ်ကြိုက်ပမာဏကို ထည့်သွင်းပါ:'
    },
    
    'manual_amount_button': {
        'en': '✏️ Enter Custom Amount',
        'my': '✏️ စိတ်ကြိုက်ပမာဏထည့်သွင်းရန်'
    },
    
    'package_choice_prompt': {
        'en': 'You selected **{price:,} MMK** package.\n\nChoose your payment method:',
        'my': 'သင် **{price:,} MMK** အစုံကို ရွေးချယ်ခဲ့သည်။\n\nသင့်ငွေပေးချေမှုနည်းလမ်းကို ရွေးချယ်ပါ:'
    },
    
    'ask_manual_amount': {
        'en': 'Please enter the amount in MMK (minimum 500 MMK):',
        'my': 'MMK ဖြင့် ပမာဏကို ထည့်သွင်းပါ (အနည်းဆုံး ၅၀၀ MMK):'
    },
    
    'min_amount_prompt': {
        'en': 'Minimum amount is 500 MMK. Please try again.',
        'my': 'အနည်းဆုံးပမာဏမှာ ၅၀၀ MMK ဖြစ်သည်။ ကျေးဇူးပြု၍ ထပ်မံကြိုးစားပါ။'
    },
    
    'invalid_amount_prompt': {
        'en': 'Invalid amount. Please enter numbers only.',
        'my': 'မမှန်ကန်သောပမာဏ။ ကျေးဇူးပြု၍ နံပါတ်များသာ ထည့်သွင်းပါ။'
    },
    
    'manual_choice_prompt': {
        'en': 'You want to buy **{price:,} MMK** worth of credits.\n\nChoose your payment method:',
        'my': 'သင် **{price:,} MMK** တန်ဖိုးရှိ ခရက်ဒစ်များကို ဝယ်ယူလိုပါသည်။\n\nသင့်ငွေပေးချေမှုနည်းလမ်းကို ရွေးချယ်ပါ:'
    },
    
    'payment_instructions': {
        'en': '💳 **Payment Instructions** 💳\n\n**Order ID:** `{order_id}`\n**Amount:** {price:,} MMK\n**Credits:** {credits:.2f}\n\n**{method} Number:** `{number}`\n\nPlease send **{price:,} MMK** to the above number and upload a screenshot of the payment confirmation.',
        'my': '💳 **ငွေပေးချေမှုလမ်းညွှန်ချက်များ** 💳\n\n**အမှာနံပါတ်:** `{order_id}`\n**ပမာဏ:** {price:,} MMK\n**ခရက်ဒစ်များ:** {credits:.2f}\n\n**{method} နံပါတ်:** `{number}`\n\nကျေးဇူးပြု၍ အထက်နံပါတ်သို့ **{price:,} MMK** ပို့ပြီး ငွေပေးချေမှုအတည်ပြုချက်၏ screenshot ကို upload လုပ်ပါ။'
    },
    
    'session_expired': {
        'en': 'Session expired. Please start again.',
        'my': 'Session ကုန်သွားပါသည်။ ကျေးဇူးပြု၍ ထပ်မံစတင်ပါ။'
    },
    
    'payment_submitted': {
        'en': '✅ Payment screenshot submitted successfully!\n\nYour order is being reviewed. You will be notified once approved.',
        'my': '✅ ငွေပေးချေမှု screenshot ကို အောင်မြင်စွာ တင်သွင်းခဲ့သည်!\n\nသင့်အမှာကို ပြန်လည်သုံးသပ်နေပါသည်။ အတည်ပြုပြီးသည်နှင့် သင့်ကို အကြောင်းကြားပါမည်။'
    },
    
    'operation_cancelled': {
        'en': 'Operation cancelled.',
        'my': 'လုပ်ငန်းကို ပယ်ဖျက်ခဲ့သည်။'
    },
    
    'select_operator': {
        'en': '🛒 **Browse Products** 🛒\n\nSelect a mobile operator:',
        'my': '🛒 **ထုတ်ကုန်များကြည့်ရှုရန်** 🛒\n\nမိုဘိုင်းအော်ပရေတာတစ်ခုကို ရွေးချယ်ပါ:'
    },
    
    'select_category': {
        'en': '📁 **{operator}** 📁\n\nSelect a category:',
        'my': '📁 **{operator}** 📁\n\nအမျိုးအစားတစ်ခုကို ရွေးချယ်ပါ:'
    },
    
    'select_product': {
        'en': '📦 **{operator} - {category}** 📦\n\nSelect a product:',
        'my': '📦 **{operator} - {category}** 📦\n\nထုတ်ကုန်တစ်ခုကို ရွေးချယ်ပါ:'
    },
    
    'beautiful_numbers_title': {
        'en': '📞 **{operator} - Beautiful Numbers** 📞\n\nSelect a beautiful number:',
        'my': '📞 **{operator} - လှပသောနံပါတ်များ** 📞\n\nလှပသောနံပါတ်တစ်ခုကို ရွေးချယ်ပါ:'
    },
    
    'bnum_instructions_button': {
        'en': 'ℹ️ How to use Beautiful Numbers',
        'my': 'ℹ️ လှပသောနံပါတ်များကို အသုံးပြုပုံ'
    },
    
    'bnum_instructions_text': {
        'en': 'ℹ️ **How to use Beautiful Numbers** ℹ️\n\n1. Purchase a beautiful number\n2. We will deliver it to you within 24 hours\n3. You can use it as your primary number or transfer to your existing SIM\n\n**Note:** Beautiful numbers are special phone numbers with memorable patterns.',
        'my': 'ℹ️ **လှပသောနံပါတ်များကို အသုံးပြုပုံ** ℹ️\n\n1. လှပသောနံပါတ်တစ်ခုကို ဝယ်ယူပါ\n2. ၂၄ နာရီအတွင်း သင့်ထံ ပို့ပေးပါမည်\n3. သင့်အဓိကနံပါတ်အဖြစ် သုံးနိုင်သည် သို့မဟုတ် လက်ရှိ SIM သို့ လွှဲပြောင်းနိုင်သည်\n\n**မှတ်ချက်:** လှပသောနံပါတ်များမှာ မှတ်မိရလွယ်သော ပုံစံများရှိသည့် အထူးဖုန်းနံပါတ်များဖြစ်သည်။'
    },
    
    'confirm_purchase_title': {
        'en': '🛒 **Confirm Purchase** 🛒\n\n**Product:** {name}\n**Operator:** {operator}\n**Cost:** {cost:.2f} Credits\n\nProceed with purchase?',
        'my': '🛒 **ဝယ်ယူမှုအတည်ပြုရန်** 🛒\n\n**ထုတ်ကုန်:** {name}\n**အော်ပရေတာ:** {operator}\n**ကုန်ကျစရိတ်:** {cost:.2f} ခရက်ဒစ်\n\nဝယ်ယူမှုကို ဆက်လုပ်မည်လား?'
    },
    
    'insufficient_credits': {
        'en': 'Insufficient credits! Please buy more credits first.',
        'my': 'ခရက်ဒစ်မလုံလောက်ပါ! ကျေးဇူးပြု၍ အရင်ဆုံး ခရက်ဒစ်များ ပိုဝယ်ပါ။'
    },
    
    'credit_low_prompt': {
        'en': '💳 **Insufficient Credits** 💳\n\nYou need **{needed:.2f}** credits but you only have **{has:.2f}** credits.\n\nPlease buy more credits first.',
        'my': '💳 **ခရက်ဒစ်မလုံလောက်ပါ** 💳\n\nသင် **{needed:.2f}** ခရက်ဒစ် လိုအပ်သော်လည်း **{has:.2f}** ခရက်ဒစ်သာ ရှိပါသည်။\n\nကျေးဇူးပြု၍ အရင်ဆုံး ခရက်ဒစ်များ ပိုဝယ်ပါ။'
    },
    
    'delivery_bnum': {
        'en': 'We will deliver this beautiful number to you within 24 hours.',
        'my': '၂၄ နာရီအတွင်း ဤလှပသောနံပါတ်ကို သင့်ထံ ပို့ပေးပါမည်။'
    },
    
    'ask_phone_number': {
        'en': '📱 **Enter Phone Number** 📱\n\nProduct: **{name}**\nCost: **{cost:.2f}** Credits\n\nPlease enter your phone number for delivery:',
        'my': '📱 **ဖုန်းနံပါတ်ထည့်သွင်းပါ** 📱\n\nထုတ်ကုန်: **{name}**\nကုန်ကျစရိတ်: **{cost:.2f}** ခရက်ဒစ်\n\nကျေးဇူးပြု၍ ပို့ရန်အတွက် သင့်ဖုန်းနံပါတ်ကို ထည့်သွင်းပါ:'
    },
    
    'delivery_to_phone': {
        'en': 'Delivery to: {phone}',
        'my': 'ပို့ရန်: {phone}'
    },
    
    'order_submitted': {
        'en': '✅ **Order Submitted Successfully!** ✅\n\n**Order ID:** `{order_id}`\n**Product:** {name}\n**Cost:** {cost:.2f} Credits\n**Delivery Info:** {delivery_info}\n\nYour order is being processed. You will be notified once completed.',
        'my': '✅ **အမှာကို အောင်မြင်စွာ တင်သွင်းခဲ့သည်!** ✅\n\n**အမှာနံပါတ်:** `{order_id}`\n**ထုတ်ကုန်:** {name}\n**ကုန်ကျစရိတ်:** {cost:.2f} ခရက်ဒစ်\n**ပို့ရန်အချက်အလက်:** {delivery_info}\n\nသင့်အမှာကို ကိုင်တွယ်ဆောင်ရွက်နေပါသည်။ ပြီးစီးသည်နှင့် သင့်ကို အကြောင်းကြားပါမည်။'
    },
    
    'my_orders_title': {
        'en': '📋 **My Orders** 📋\n\n',
        'my': '📋 **ကျွန်ုပ်၏အမှာများ** 📋\n\n'
    },
    
    'order_line': {
        'en': '**{order_id}**\n{pkg} - {cost:.2f} C\n*{status}* | {date}\n\n',
        'my': '**{order_id}**\n{pkg} - {cost:.2f} C\n*{status}* | {date}\n\n'
    },
    
    'no_orders': {
        'en': 'No orders found.',
        'my': 'အမှာများ မတွေ့ရှိပါ။'
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    """
    Get translated text for a given key and language.
    
    Args:
        key: The text key
        lang: Language code ('en' or 'my')
        **kwargs: Variables to format into the text
    
    Returns:
        Formatted translated text
    """
    if key not in TEXTS:
        return f"[Missing: {key}]"
    
    if lang not in TEXTS[key]:
        lang = 'en'  # Fallback to English
    
    text = TEXTS[key][lang]
    
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    
    return text
