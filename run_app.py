import webview
import threading
import sys
import os
from app import app  # Ensure app.py is in the same folder!

def start_flask():
    # This runs your Flask engine on Port 5000
    # 'use_reloader=False' is critical for Desktop apps
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Start the Flask server in the background
    print("🚀 Initializing RSP Core Engine...")
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()

    # 2. Launch the Desktop Window pointing to the LOCALHOST, not a file
    # This ensures your href="/login" links actually work
    print("🖥️ Launching Desktop Interface...")
    window = webview.create_window(
        'RSP Core System', 
        'http://127.0.0.1:5000', 
        width=1200, 
        height=800,
        background_color='#030712'
    )

    webview.start()