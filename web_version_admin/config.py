import os
import sys
from pathlib import Path

# ---------- PATH RESOLUTION ----------
ASSETS_DIR_OVERRIDE = os.environ.get("CCRI_ASSETS_DIR")

def detect_assets_dir() -> Path:
    """
    Priority:
      1) CCRI_ASSETS_DIR (env)
      2) <dir_of_running_pyz>/web_version (next to the pyz)
      3) directory of this source file (dev/admin tree)
    """
    if ASSETS_DIR_OVERRIDE:
        return Path(ASSETS_DIR_OVERRIDE).resolve()

    # Locate directory relative to the executed script/zipapp
    pyz_dir = Path(sys.argv[0]).resolve().parent
    candidate = pyz_dir / "web_version"
    if candidate.is_dir():
        return candidate

    # Fallback to the physical location of this file inside the source tree
    return Path(__file__).resolve().parent

# Establish foundational project paths using clean Path properties
server_dir      = detect_assets_dir()
BASE_DIR        = server_dir.parent

# Flask explicitly expects string path inputs for directory registrations
template_folder = str(server_dir / "templates")
static_folder   = str(server_dir / "static")

# ---------- MODE CONFIGURATION ----------
DEBUG_MODE = os.environ.get("CCRI_DEBUG", "0") == "1"

# Base Mode: Admin vs Student
base_mode = os.environ.get("CCRI_CTF_MODE", "").strip().lower()
if not base_mode:
    # server_dir.name handles the string extraction natively (replacing basename)
    base_mode = "admin" if server_dir.name == "web_version_admin" else "student"

has_admin = (BASE_DIR / "web_version_admin").is_dir()
if base_mode == "admin" and not has_admin:
    print("⚠️ Admin mode requested but admin assets missing; forcing STUDENT mode.")
    base_mode = "student"

os.environ["CCRI_CTF_MODE"] = base_mode

# Folders containing challenge data
GUIDED_DIR = str(BASE_DIR / "challenges")
SOLO_DIR   = str(BASE_DIR / "challenges_solo")

def detect_available_modes():
    modes = []
    if Path(GUIDED_DIR).is_dir():
        modes.append("regular")
    if Path(SOLO_DIR).is_dir():
        modes.append("solo")
    return modes

AVAILABLE_MODES = detect_available_modes()
DEFAULT_MODE = "regular" if "regular" in AVAILABLE_MODES else ("solo" if "solo" in AVAILABLE_MODES else None)