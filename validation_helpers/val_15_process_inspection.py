#!/usr/bin/env python3

import sys
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "15_ProcessInspection"

def validate_flag_in_ps_dump(ps_path: Path, expected_flag: str) -> bool:
    """Scans the ps_dump file for the expected flag."""
    if not ps_path.is_file():
        print(f"❌ ERROR: ps_dump.txt not found at {ps_path}", file=sys.stderr)
        return False

    try:
        # Read file and look for flag
        with ps_path.open("r", encoding="utf-8", errors="ignore") as f:
            if any(expected_flag in line for line in f):
                print(f"✅ Validation success: found flag {expected_flag}")
                return True
    except Exception as e:
        print(f"❌ ERROR reading ps_dump: {e}", file=sys.stderr)
        return False

    print(f"❌ Validation failed: flag {expected_flag} not found.", file=sys.stderr)
    return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Get path using our shared helper from common.py
    # We locate the parent directory of the challenge file to find ps_dump.txt
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    ps_path = base_file.parent / "ps_dump.txt"

    return validate_flag_in_ps_dump(ps_path, expected_flag)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)