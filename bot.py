# bot.py
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ConversationHandler,
    MessageHandler, filters, ContextTypes, PicklePersistence,
)

import config
import database as db
import handlers
import admin
import middleware

async def post_init(application: Application):
    await db.setup_database()
    application.bot_data["ADMIN_IDS"] = config.ADMIN_IDS
    commands_user = [BotCommand("start", "🚀 Start / Main Menu"), BotCommand("cancel", "❌ Cancel")]
    commands_admin = commands_user + [BotCommand("admin", "👑 Admin Panel")]
    for admin_id in config.ADMIN_IDS:
        try: await application.bot.set_my_commands(commands_admin, scope={'type': 'chat', 'chat_id': admin_id})
        except Exception as e: config.logger.warning(f"Could not set commands for admin {admin_id}: {e}")
    await application.bot.set_my_commands(commands_user)
    config.logger.info("Database setup complete and bot commands set dynamically.")

def main() -> None:
    persistence = PicklePersistence(filepath="bot_persistence")
    app = (
        Application.builder()
        .token(config.TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .build()
    )

    shared_fallbacks = [
        CommandHandler('cancel', handlers.universal_cancel),
        CommandHandler('start', handlers.start),
        CallbackQueryHandler(handlers.universal_cancel, pattern='^cancel_flow$'),
        CallbackQueryHandler(handlers.show_main_menu, pattern='^main_menu$'),
    ]

    # --- USER CONVERSATIONS ---
    credit_purchase_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.credits_start, pattern='^credits_buy_start$')],
        states={
            handlers.SELECTING_CREDIT_OPTION: [
                CallbackQueryHandler(handlers.credits_package_selected, pattern='^credits_pkg_'),
                CallbackQueryHandler(handlers.credits_manual_start, pattern='^credits_manual$'),
            ],
            handlers.AWAITING_MANUAL_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.credits_manual_amount_received)],
            handlers.SELECTING_PAYMENT: [
                CallbackQueryHandler(handlers.credits_payment_method_selected, pattern='^pay_'),
                CallbackQueryHandler(handlers.credits_start, pattern='^credits_buy_start$')
            ],
            handlers.AWAITING_SCREENSHOT: [MessageHandler(filters.PHOTO, handlers.credits_screenshot_received)],
        },
        fallbacks=shared_fallbacks, name="credit_purchase_flow", persistent=True, per_message=False,
    )
    product_shop_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.shop_start, pattern='^shop_main$')],
        states={
            handlers.SHOP_OPERATOR: [CallbackQueryHandler(handlers.shop_operator_selected, pattern='^shop_op_')],
            handlers.SHOP_CATEGORY: [
                CallbackQueryHandler(handlers.shop_category_selected, pattern='^shop_cat_'),
                CallbackQueryHandler(handlers.shop_start, pattern='^shop_main$')
            ],
            handlers.SHOP_PRODUCT_LIST: [
                CallbackQueryHandler(handlers.shop_beautiful_number_info, pattern='^shop_bnum_info$'),
                CallbackQueryHandler(handlers.shop_category_selected, pattern='^shop_page_'),
                CallbackQueryHandler(handlers.shop_product_selected, pattern='^shop_(prod|bnum)_'),
                CallbackQueryHandler(handlers.shop_operator_selected, pattern='^shop_op_'),
                CallbackQueryHandler(handlers.shop_category_selected, pattern='^shop_cat_'),
            ],
            handlers.SHOP_CONFIRM: [
                CallbackQueryHandler(handlers.shop_confirm_purchase, pattern='^buy_confirm_'),
                CallbackQueryHandler(handlers.shop_cancel_to_category, pattern='^buy_cancel_'),
            ],
            handlers.AWAITING_PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.shop_phone_number_received)]
        },
        fallbacks=shared_fallbacks, name="product_shop_flow", persistent=True, per_message=False,
    )
    my_orders_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.my_orders_start, pattern='^orders_view_')],
        states={ 
            handlers.VIEWING_ORDERS: [
                CallbackQueryHandler(handlers.show_main_menu, pattern='^main_menu$'),
                CallbackQueryHandler(handlers.my_orders_start, pattern='^orders_view_')
            ] 
        },
        fallbacks=shared_fallbacks, name="my_orders_view", persistent=True,
    )

    # --- ADMIN CONVERSATIONS ---
    admin_command_filter = filters.User(user_id=config.ADMIN_IDS)
    admin_user_id_input_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin.manage_user_start, pattern='^admin_manage_user_start$'),
            CallbackQueryHandler(admin.broadcast_one_start, pattern='^admin_broadcast_one$'),
        ],
        states={
            admin.AWAITING_USER_ID_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.received_user_id_input)],
            admin.AWAITING_BROADCAST_MESSAGE_ONE: [MessageHandler(filters.ALL & ~filters.COMMAND, admin.broadcast_one_received)],
        },
        fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="admin_user_id_input_flow"
    )
    adjust_credits_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.adjust_user_credits_start, pattern='^admin_user_credits_')], states={admin.AWAITING_CREDIT_ADJUSTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.adjust_user_credits_received)]}, fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="adjust_credits_flow")
    purge_user_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.purge_user_start, pattern='^admin_user_purge_')], states={admin.AWAITING_PURGE_CONFIRMATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.purge_user_confirm)]}, fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="purge_user_flow")
    broadcast_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.broadcast_start, pattern='^admin_broadcast_start$')], states={admin.AWAITING_BROADCAST_MESSAGE_ALL: [MessageHandler(filters.ALL & ~filters.COMMAND, admin.broadcast_all_received)]}, fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="broadcast_flow")
    admin_add_bnum_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.add_bnum_start, pattern='^admin_addbnum_start$')], states={admin.AWAITING_BNUM_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.add_bnum_details_received)]}, fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="admin_add_bnum_flow")
    admin_add_prod_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.add_product_start, pattern='^admin_addprod_start$')], states={admin.AWAITING_NEW_PRODUCT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.add_product_details_received)]}, fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="admin_add_prod_flow")
    admin_edit_prod_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin.edit_product_start, pattern='^admin_edit_start$')],
        states={
            admin.AWAITING_PRODUCT_ID_TO_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.edit_product_id_received)],
            admin.AWAITING_EDIT_CHOICE: [CallbackQueryHandler(admin.edit_product_choice, pattern='^edit_prod_')],
            admin.AWAITING_NEW_PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.edit_product_new_value_received)],
            admin.AWAITING_NEW_PRODUCT_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.edit_product_new_value_received)],
            admin.AWAITING_NEW_PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.edit_product_new_value_received)],
        },
        fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="admin_edit_prod_flow"
    )
    admin_delete_prod_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(admin.delete_product_start, pattern='^admin_delete_start$')],
        states={
            admin.AWAITING_PRODUCT_ID_TO_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin.delete_product_id_received)],
            admin.AWAITING_DELETE_CONFIRMATION: [CallbackQueryHandler(admin.delete_product_confirmation, pattern='^delete_confirm_')],
        },
        fallbacks=[CommandHandler('cancel', admin.admin_cancel)], name="admin_delete_prod_flow"
    )
    view_all_orders_conv = ConversationHandler(entry_points=[CallbackQueryHandler(admin.view_all_orders, pattern='^admin_view_orders_')], states={}, fallbacks=[CallbackQueryHandler(admin.admin_panel, pattern='^admin_panel$')], name="view_all_orders_flow")
    
    # Add Handlers
    app.add_handler(credit_purchase_conv)
    app.add_handler(product_shop_conv)
    app.add_handler(my_orders_conv)
    app.add_handler(admin_add_bnum_conv)
    app.add_handler(admin_add_prod_conv)
    app.add_handler(admin_edit_prod_conv)
    app.add_handler(admin_delete_prod_conv)
    app.add_handler(view_all_orders_conv)
    app.add_handler(admin_user_id_input_conv)
    app.add_handler(adjust_credits_conv)
    app.add_handler(purge_user_conv)
    app.add_handler(broadcast_conv)

    # Standalone Handlers
    app.add_handler(CommandHandler('start', handlers.start))
    app.add_handler(CommandHandler('admin', admin.admin_panel, filters=admin_command_filter))
    app.add_handler(CallbackQueryHandler(handlers.start, pattern='^check_join_status$'))
    app.add_handler(CallbackQueryHandler(admin.admin_panel, pattern='^admin_panel$'))
    app.add_handler(CallbackQueryHandler(admin.view_all_products, pattern='^admin_view_prods_'))
    app.add_handler(CallbackQueryHandler(handlers.change_language, pattern='^change_lang$'))
    app.add_handler(CallbackQueryHandler(handlers.show_main_menu, pattern='^main_menu_refresh$'))
    app.add_handler(CallbackQueryHandler(admin.approval_handler, pattern='^admin_(approve|reject)_'))
    app.add_handler(CallbackQueryHandler(admin.ban_unban_user, pattern='^admin_user_(ban|unban)_'))
    app.add_handler(CallbackQueryHandler(admin.broadcast_all_start, pattern='^admin_broadcast_all$'))
    
    app.add_error_handler(handlers.error_handler)

    config.logger.info("Bot is starting with persistence enabled...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()