# config.py
import logging
import colorlog # New import

# === Force Join Configuration ===
FORCE_JOIN_CHANNEL = "@AtomPointPackage"  # Set to None to disable.

# --- BOT CONFIGURATION ---
TOKEN = '8105753048:AAF588KJ1VuLV48JbtCrlsdRswf_4iKsJPY'  # Replace with your token
ADMIN_IDS = {123456789, 6158106622}  # Replace with your actual admin IDs.

# --- CHANNEL CONFIGURATION ---
CREDIT_REVIEW_CHANNEL = "@paymentrequestch"
ORDER_FULFILLMENT_CHANNEL = "@songbank12"

# --- PAYMENT CONFIGURATION ---
KBZ_PAY_NUMBER = "09883249943"
WAVE_PAY_NUMBER = "09883249943"
CREDIT_PER_MMK = 1 / 100

# --- PRE-SET CREDIT PACKAGES ---
CREDIT_PACKAGES = [
    {'price': 1000, 'credits': 10},
    {'price': 3000, 'credits': 30},
    {'price': 5000, 'credits': 50}
]

# --- UPGRADED COLORFUL LOGGING SETUP ---
def setup_logger():
    """Sets up a colorful and informative logger."""
    handler = colorlog.StreamHandler()
    
    # Define the format with log colors and emojis
    log_format = (
        '%(log_color)s%(asctime)s - '
        '%(levelname)-8s - '
        '%(purple)s[%(filename)s:%(lineno)d]%(reset)s - '
        '%(message_log_color)s%(message)s'
    )
    
    # Define custom colors for the message part of the log
    formatter = colorlog.ColoredFormatter(
        log_format,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={
            'message': {
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        },
        reset=True,
        style='%'
    )
    handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers and add our new one
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.addHandler(handler)
    
    # Keep third-party libraries less verbose
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)

    return logging.getLogger("main_bot_logger")

# Initialize the logger
logger = setup_logger()