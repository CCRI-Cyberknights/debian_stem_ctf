#!/usr/bin/env python3

import sys
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "11_HiddenFlag"

def validate_hidden_flag(directory: Path, expected_flag: str) -> bool:
    """Recursively searches for the flag in a directory."""
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            try:
                # Using errors="ignore" to avoid crashes on binary files in the junk folder
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                if expected_flag in content:
                    print(f"✅ Validation success: found flag {expected_flag} in {file_path}")
                    return True
            except Exception:
                continue
    return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Path resolution: We target the 'junk' directory
    # get_challenge_file returns the path to a specific file, so we get its parent
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    junk_dir = base_file.parent / "junk"

    if not junk_dir.is_dir():
        print(f"❌ ERROR: Expected directory not found: {junk_dir}", file=sys.stderr)
        return False

    if validate_hidden_flag(junk_dir, expected_flag):
        return True
    
    print(f"❌ Validation failed: flag {expected_flag} not found in any files.", file=sys.stderr)
    return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)