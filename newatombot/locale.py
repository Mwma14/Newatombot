# locale.py

# This dictionary holds all the text for the bot.
# All special Markdown characters (*, _, etc.) have been removed, except for ``.
LANG = {
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
        'insufficient_credits': "❌ Insufficient Credits!",
        'session_expired': "⚠️ Your session has expired. Please start the action again.",
        'select_operator': "Please select an operator:",
        'select_category': "You selected {operator}. Please choose a product category:",
        'select_product': "{operator} - {category}\nSelect a product to purchase.",
        'beautiful_numbers_title': "{operator} - Beautiful Numbers\nSelect a number to purchase.",
        'bnum_instructions_button': "ℹ️ How to Buy (Instructions)",
        'confirm_purchase_title': "Confirm Purchase\n\nItem: {name}\nOperator: {operator}\n"
                                  "Cost: {cost:.2f} Credits\n\n",
        'proceed_prompt': "Confirm Purchase",
        'credit_low_prompt': "Credit Balance Too Low\n\nYou need {needed:.2f} C but only have {has:.2f} C."
                             "\n\nPlease buy more credits to proceed.",
        'ask_phone_number': "📱 Enter Phone Number\n\nYou are ordering: `{name}`\nCost: `{cost:.2f}` Credits\n\n"
                            "Please send the phone number to receive the product (e.g., 09...).",
        'order_submitted': "✅ Order Submitted!\n\nOrder ID: `{order_id}`\nItem: {name}\n"
                           "Cost: {cost:.2f} Credits\n{delivery_info}\n\nAn admin will process your order shortly.",
        'delivery_to_phone': "To Phone: `{phone}`",
        'delivery_bnum': "Delivery: Contact admin per instructions.",
        'buy_credits_prompt': "💰 Buy Credits\n\nThe rate is 100 MMK = 1 Credit.\n\n"
                              "Please select a package or enter a manual amount.",
        'manual_amount_button': "✍️ Enter Manual Amount",
        'ask_manual_amount': "Please enter the amount in MMK you wish to deposit.\n(e.g., `2000`)",
        'min_amount_prompt': "Minimum amount is 500 MMK. Please try again.",
        'invalid_amount_prompt': "Invalid amount. Please send a number only.",
        'package_choice_prompt': "You've selected the package for {price:,} MMK.\nPlease choose a payment method:",
        'manual_choice_prompt': "You've chosen to deposit {price:,} MMK.\nPlease choose a payment method:",
        'payment_instructions': "Payment Instructions\n\nOrder ID: `{order_id}`\nAmount to Pay: {price:,} MMK\n"
                                "Credits to Receive: {credits:.2f} C\n\n1. Send the exact amount to `{number}` "
                                "via {method}.\n2. Take a screenshot of the successful transaction receipt.\n"
                                "3. Send that screenshot back to me in this chat.",
        'payment_submitted': "✅ Payment Submitted! Your payment is now under review by an admin. "
                             "You will be notified upon approval.",
        'my_orders_title': "📋 My Orders\n",
        'pending_orders_header': "\n⏳ Pending Orders\n" + "—"*20 + "\n",
        'history_orders_header': "\n📖 Order History\n" + "—"*20 + "\n",
        'no_orders': "\nYou have no orders.",
        'order_line': "`{order_id}`\n  `{pkg}` ({status})\n  Cost: {cost:.2f} C | {date}\n\n",
        'bnum_instructions_text': """
Beautiful Number Purchase Guide

You are buying a special phone number. The process is as follows:
1. Complete the purchase using your credits in this bot.
2. Your order will be sent to our admin team.
3. Contact our admin directly on Telegram to arrange delivery.
4. Admin Account: @CEO_METAVERSE
5. Tell the admin your Order ID (which you'll receive after purchase) and your delivery location. The number SIM will be sent to you via a delivery service.
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
        'operation_cancelled': "❌ လုပ်ဆောင်မှုအား ပယ်ဖျက်လိုက်ပါသည်။",
        'insufficient_credits': "❌ Credit မလုံလောက်ပါ။",
        'session_expired': "⚠️ လုပ်ဆောင်မှုအချိန် ကျော်လွန်သွားပါသဖြင့် အစမှပြန်လည် စတင်ပါ။",
        'select_operator': "ကျေးဇူးပြု၍ Operator တစ်ခု ရွေးချယ်ပါ:",
        'select_category': "{operator} ကို ရွေးထားပါသည်။ ကျေးဇူးပြု၍ အမျိုးအစားတစ်ခု ရွေးပါ:",
        'select_product': "{operator} - {category}\nဝယ်ယူရန် ပစ္စည်းတစ်ခု ရွေးချယ်ပါ:",
        'beautiful_numbers_title': "{operator} - နံပါတ်လှများ\nဝယ်ယူရန် နံပါတ်တစ်ခု ရွေးချယ်ပါ:",
        'bnum_instructions_button': "ℹ️ ဝယ်ယူရန် လမ်းညွှန်",
        'confirm_purchase_title': "ဝယ်ယူမှုအား အတည်ပြုပါ\n\nပစ္စည်း: {name}\nOperator: {operator}\n"
                                  "ကုန်ကျစရိတ်: {cost:.2f} Credits\n\n",
        'proceed_prompt': "ဝယ်ယူမှုအား အတည်ပြုပါ",
        'credit_low_prompt': "Credit လက်ကျန် နည်းနေပါသည်\n\nလိုအပ်သော Credit: {needed:.2f} C\n"
                             "သင့်လက်ကျန်: {has:.2f} C\n\nကျေးဇူးပြု၍ Credit ထပ်မံဖြည့်တင်းပါ။",
        'ask_phone_number': "📱 ဖုန်းနံပါတ် ထည့်ပါ\n\nသင်ဝယ်ယူသော ပစ္စည်း: `{name}`\nကုန်ကျငွေ: `{cost:.2f}` Credits\n\n"
                            "ပစ္စည်းလက်ခံမည့် ဖုန်းနံပါတ်အား ထည့်ပေးပါ (ဥပမာ 09...).",
        'order_submitted': "✅ Order တင်ပြီးပါပြီ!\n\nOrder ID: `{order_id}`\nပစ္စည်း: {name}\n"
                           "ကုန်ကျငွေ: {cost:.2f} Credits\n{delivery_info}\n\nAdmin မှ မကြာမီ ဆောင်ရွက်ပေးပါမည်။",
        'delivery_to_phone': "ပို့ရန်ဖုန်း: `{phone}`",
        'delivery_bnum': "ပို့ဆောင်ရန်: လမ်းညွှန်အတိုင်း Admin ကိုဆက်သွယ်ပါ။",
        'buy_credits_prompt': "💰 Credit ဝယ်ယူရန်\n\nနှုန်းထားမှာ 100 MMK = 1 Credit ဖြစ်ပါသည်။\n\n"
                              "Package တစ်ခုရွေးပါ သို့မဟုတ် ပမာဏ ကိုယ်တိုင်ရိုက်ထည့်ပါ။",
        'manual_amount_button': "✍️ ပမာဏ ကိုယ်တိုင်ရိုက်ထည့်ရန်",
        'ask_manual_amount': "သင်ဖြည့်လိုသော ပမာဏကို MMK ဖြင့် ရိုက်ထည့်ပါ\n(ဥပမာ `2000`)",
        'min_amount_prompt': "အနည်းဆုံး 500 MMK ဖြည့်ရပါမည်။",
        'invalid_amount_prompt': "ပမာဏ မှားယွင်းနေပါသည်။ ဂဏန်း သီးသန့်သာ ရိုက်ထည့်ပါ။",
        'package_choice_prompt': "{price:,} MMK တန် Package ကို ရွေးချယ်ထားပါသည်။\nငွေပေးချေမှုနည်းလမ်း ရွေးချယ်ပါ။",
        'manual_choice_prompt': "{price:,} MMK ဖြည့်ရန် ရွေးချယ်ထားပါသည်။\nငွေပေးချေမှုနည်းလမ်း ရွေးချယ်ပါ။",
        'payment_instructions': "ငွေပေးချေရန် လမ်းညွှန်\n\nOrder ID: `{order_id}`\nပေးချေရမည့် ပမာဏ: {price:,} MMK\n"
                                "ရရှိမည့် Credit: {credits:.2f} C\n\n၁။ `{number}` သို့ {method} မှတစ်ဆင့် ငွေအတိအကျ လွှဲပေးပါ။\n"
                                "၂။ ငွေလွှဲအောင်မြင်သော ဘောင်ချာကို Screenshot ရိုက်ပါ။\n"
                                "၃။ ထို Screenshot ကို ဤနေရာတွင် ပြန်လည်ပေးပို့ပါ။",
        'payment_submitted': "✅ ငွေပေးချေမှု တင်သွင်းပြီးပါပြီ! Admin မှ စစ်ဆေးပြီးပါက သင့်အား အကြောင်းကြားပါမည်။",
        'my_orders_title': "📋 ကျွန်ုပ်၏ Orders\n",
        'pending_orders_header': "\n⏳ ဆောင်ရွက်ဆဲ Orders\n" + "—"*20 + "\n",
        'history_orders_header': "\n📖 ပြီးခဲ့သော Orders\n" + "—"*20 + "\n",
        'no_orders': "\nသင့်တွင် Order တစ်ခုမှ မရှိသေးပါ။",
        'order_line': "`{order_id}`\n  `{pkg}` ({status})\n  ကုန်ကျငွေ: {cost:.2f} C | {date}\n\n",
        'bnum_instructions_text': """
နံပါတ်လှ ဝယ်ယူခြင်း လမ်းညွှန်

သင်သည် အထူးဖုန်းနံပါတ်တစ်ခုကို ဝယ်ယူနေပါသည်။ လုပ်ငန်းစဉ်မှာ အောက်ပါအတိုင်း ဖြစ်သည်-
၁။ ဤဘော့တ်တွင် သင့် credit များဖြင့် ဝယ်ယူမှုကို အပြီးသတ်ပါ။
၂။ သင်၏ Order ကို ကျွန်ုပ်တို့၏ admin အဖွဲ့ထံ ပေးပို့ပါမည်။
၃။ ပစ္စည်းပို့ဆောင်ရန် ကျွန်ုပ်တို့၏ admin ကို Telegram မှ တိုက်ရိုက် ဆက်သွယ်ပါ။
၄။ Admin Account: @CEO_METAVERSE
၅။ admin အား သင်၏ Order ID (ဝယ်ယူပြီးနောက် သင်ရရှိမည့်) နှင့် ပို့ဆောင်ပေးရမည့် လိပ်စာကို ပြောပြပါ။ နံပါတ် SIM ကတ်ကို ပို့ဆောင်ရေးဝန်ဆောင်မှုဖြင့် သင့်ထံ ပေးပို့ပါမည်။
"""
    }
}

def get_text(key: str, lang: str = 'en', **kwargs) -> str:
    if lang not in LANG: lang = 'en'
    text = LANG.get(lang, LANG['en']).get(key, f"_{key}_")
    if kwargs: return text.format(**kwargs)
    return text