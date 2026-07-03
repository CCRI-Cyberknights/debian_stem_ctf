#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "12_QRCodes"

def check_dependencies():
    """Fail-fast check for zbarimg."""
    if not shutil.which("zbarimg"):
        print("❌ ERROR: 'zbarimg' is not installed. Run 'sudo apt install zbar-tools'.", file=sys.stderr)
        sys.exit(1)

def decode_qr(file_path: Path) -> str:
    """Uses zbarimg to decode QR code."""
    try:
        result = subprocess.run(
            ["zbarimg", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Error decoding QR code: {e}", file=sys.stderr)
        return ""

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    check_dependencies()

    # Path resolution
    # get_challenge_file returns the path to one of the files; we use the parent dir
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    challenge_dir = base_file.parent

    # Expecting 5 QR codes
    qr_codes = [challenge_dir / f"qr_0{i}.png" for i in range(1, 6)]

    for qr in qr_codes:
        if not qr.is_file():
            print(f"❌ ERROR: QR image missing: {qr}", file=sys.stderr)
            return False
            
        decoded = decode_qr(qr)
        if expected_flag in decoded:
            print(f"✅ Validation success: found flag {expected_flag} in {qr.name}")
            return True

    print(f"❌ Validation failed: flag {expected_flag} not found in any QR code.", file=sys.stderr)
    return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)