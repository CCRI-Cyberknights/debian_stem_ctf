import sys
import logging
import os
from flask import Flask

import config
from fake_services import start_all_services
from routes import bp

# ---------- BOOTSTRAP ----------
sys.dont_write_bytecode = True

# Make sure we can import Challenge/ChallengeList from BASE_DIR
if config.BASE_DIR not in sys.path:
    sys.path.insert(0, config.BASE_DIR)

# Configure Logging
logging.basicConfig(level=logging.DEBUG if config.DEBUG_MODE else logging.INFO)

print(f"📖 Using template folder at: {config.template_folder}")
print(f"DEBUG: Base mode = {config.base_mode}")
print(f"🧭 AVAILABLE_MODES = {config.AVAILABLE_MODES} | DEFAULT_MODE = {config.DEFAULT_MODE}")

# Initialize Flask
app = Flask(__name__, template_folder=config.template_folder, static_folder=config.static_folder)
app.secret_key = "super_secret_key"

# Register Blueprints
app.register_blueprint(bp)

# === Start Server ===
if __name__ == '__main__':
    # 🛡️ WERKZEUG AUTO-RELOADER GUARD
    # When Flask debug is active, Werkzeug executes this main block twice.
    # This check ensures fake service threads only bind to ports inside the active child runtime.
    if not config.DEBUG_MODE or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_all_services(config.AVAILABLE_MODES)
    else:
        logging.info("ℹ️ Master reloader active. Awaiting child runtime for service port binding.")

    print(f"🚀 {config.base_mode.capitalize()} Hub running on http://127.0.0.1:5000")
    
    # Linked dynamically to config profile to support safe hot-reloads during dev
    app.run(host='127.0.0.1', port=5000, debug=config.DEBUG_MODE, threaded=True)