import sys
import os
from app import app  # Ensure app.py is in the same folder!

def start_flask():
    # This runs your Flask engine on Port 5000
    # 'use_reloader=False' is critical for Desktop apps
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "RSP System Running 🚀"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


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
