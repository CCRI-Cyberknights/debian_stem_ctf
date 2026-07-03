#!/usr/bin/env python3

import sys
import shutil
import subprocess
from pathlib import Path
from common import find_project_root, load_unlock_data, get_ctf_mode, get_challenge_file

CHALLENGE_ID = "01_Stego"

def check_dependencies():
    """Fail-fast check for required tools."""
    if not shutil.which("steghide"):
        print("❌ ERROR: 'steghide' is not installed. Run 'sudo apt install steghide'.", file=sys.stderr)
        sys.exit(1)

def run_steghide(password: str, image_path: Path, output_path: Path) -> bool:
    """Extracts data using steghide."""
    try:
        # -f forces overwrite, -p provides the password
        cmd = ["steghide", "extract", "-sf", str(image_path), "-xf", str(output_path), "-p", password, "-f"]
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"❌ Steghide execution error: {e}", file=sys.stderr)
        return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)

    password = unlock.get("last_password")
    real_flag = unlock.get("real_flag")

    if not password or not real_flag:
        print(f"❌ ERROR: Unlock metadata missing for {CHALLENGE_ID}.", file=sys.stderr)
        return False

    # Get path using our shared helper
    image_path = get_challenge_file(root, CHALLENGE_ID, unlock)
    output_path = image_path.parent / "decoded_message.txt"

    if not image_path.is_file():
        print(f"❌ ERROR: Image file not found at {image_path}", file=sys.stderr)
        return False

    # Validate and cleanup
    try:
        check_dependencies()
        
        if not run_steghide(password, image_path, output_path):
            print(f"❌ Validation failed: could not extract with password '{password}'", file=sys.stderr)
            return False

        # Verify content
        extracted_text = output_path.read_text(errors="ignore")
        if real_flag in extracted_text:
            print(f"✅ Success! Found flag: {real_flag}")
            return True
        else:
            print("❌ Validation failed: Extracted data did not contain the real flag.", file=sys.stderr)
            return False

    finally:
        # Cleanup temporary extraction artifact
        output_path.unlink(missing_ok=True)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)