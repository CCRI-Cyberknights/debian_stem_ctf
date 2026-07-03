#!/usr/bin/env python3

import sys
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "03_ROT13"

def rot13(text: str) -> str:
    """Apply ROT13 cipher to input text."""
    result = []
    for c in text:
        if "a" <= c <= "z":
            result.append(chr((ord(c) - ord("a") + 13) % 26 + ord("a")))
        elif "A" <= c <= "Z":
            result.append(chr((ord(c) - ord("A") + 13) % 26 + ord("A")))
        else:
            result.append(c)
    return "".join(result)

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
        print(f"❌ ERROR: Cipher file not found at {input_path}", file=sys.stderr)
        return False

    try:
        # Decode the file line by line
        lines = input_path.read_text(encoding="utf-8").splitlines()
        decoded = "\n".join(rot13(line) for line in lines)
    except Exception as e:
        print(f"❌ Failed to read or decode cipher file: {e}", file=sys.stderr)
        return False

    if real_flag in decoded:
        print(f"✅ Validation success: found flag {real_flag}")
        return True
    else:
        print(f"❌ Validation failed: flag {real_flag} not found in decoded content", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)