#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "10_Metadata"

def check_dependencies():
    """Fail-fast check for required CLI tools."""
    if not shutil.which("exiftool"):
        print("❌ ERROR: 'exiftool' is not installed. Run 'sudo apt install libimage-exiftool-perl'.", file=sys.stderr)
        sys.exit(1)

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    check_dependencies()

    # Get path using our shared helper
    target_image = get_challenge_file(root, CHALLENGE_ID, unlock)

    if not target_image.is_file():
        print(f"❌ ERROR: File not found: {target_image}", file=sys.stderr)
        return False

    try:
        # Run exiftool and inspect output
        result = subprocess.run(
            ["exiftool", str(target_image)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        if expected_flag in result.stdout:
            print(f"✅ Validation success: found flag {expected_flag}")
            return True
        else:
            print(f"❌ Validation failed: flag {expected_flag} not found in metadata.", file=sys.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: exiftool failed to run: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)