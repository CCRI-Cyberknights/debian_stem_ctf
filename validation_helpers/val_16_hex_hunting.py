#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "16_HexHunting"

def check_dependencies():
    """Ensure strings utility is available."""
    if not shutil.which("strings"):
        print("❌ ERROR: 'strings' utility not found.", file=sys.stderr)
        sys.exit(1)

def validate_flag_in_binary(binary_path: Path, expected_flag: str) -> bool:
    """Checks for flag in binary via strings and raw byte search."""
    if not binary_path.is_file():
        print(f"❌ ERROR: Binary file not found at {binary_path}", file=sys.stderr)
        return False

    # 1. Check strings output
    try:
        result = subprocess.run(
            ["strings", str(binary_path)],
            stdout=subprocess.PIPE, 
            text=True, 
            check=True
        )
        if expected_flag in result.stdout:
            print(f"✅ Found flag in strings output: {expected_flag}")
            return True
    except subprocess.CalledProcessError:
        # Fallback to raw check if strings fails
        pass

    # 2. Check raw bytes
    try:
        if expected_flag.encode("utf-8") in binary_path.read_bytes():
            print(f"✅ Found flag in raw bytes: {expected_flag}")
            return True
    except Exception as e:
        print(f"❌ Error reading binary file: {e}", file=sys.stderr)

    print(f"❌ Validation failed: flag {expected_flag} not found.", file=sys.stderr)
    return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    check_dependencies()
    
    # Path resolution using shared helper
    binary_path = get_challenge_file(root, CHALLENGE_ID, unlock)
    
    return validate_flag_in_binary(binary_path, expected_flag)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)