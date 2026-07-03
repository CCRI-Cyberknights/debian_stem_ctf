#!/usr/bin/env python3

import base64
import sys
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "02_Base64"

def decode_file(input_path: Path) -> str:
    """Reads and base64 decodes the file content."""
    try:
        encoded = input_path.read_text(encoding="utf-8").strip()
        return base64.b64decode(encoded).decode("utf-8").strip()
    except Exception as e:
        print(f"❌ Error decoding base64: {e}", file=sys.stderr)
        return ""

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    real_flag = unlock.get("real_flag")

    if not real_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Get path using our shared helper from common.py
    input_path = get_challenge_file(root, CHALLENGE_ID, unlock)

    if not input_path.is_file():
        print(f"❌ Challenge file not found: {input_path}", file=sys.stderr)
        return False

    decoded = decode_file(input_path)
    
    if real_flag in decoded:
        print(f"✅ Validation success: found flag {real_flag}")
        return True
    else:
        print("❌ Validation failed: flag not found in decoded content", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)