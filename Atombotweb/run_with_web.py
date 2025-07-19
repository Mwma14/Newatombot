
import threading
import time
import subprocess
import sys

def run_bot():
    """Run the Telegram bot"""
    print("Starting Telegram bot...")
    subprocess.run([sys.executable, "bot.py"])

def run_web():
    """Run the web application"""
    print("Starting web application...")
    time.sleep(5)  # Wait for bot to initialize
    subprocess.run([sys.executable, "web_app.py"])

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start web app in main thread
    run_web()
