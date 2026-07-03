#!/usr/bin/env python3

import sys
import re
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "08_FakeAuthLog"
REGEX_PATTERN = r"\bCCRI-[A-Z0-9]{4}-\d{4}\b"

def scan_for_flags(log_path: Path, regex: str) -> list[str]:
    """Scans log file for matches against the flag regex."""
    try:
        with log_path.open("r", encoding="utf-8", errors="ignore") as f:
            return [line.strip() for line in f if re.search(regex, line)]
    except Exception as e:
        print(f"❌ ERROR while scanning log: {e}", file=sys.stderr)
        return []

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Get path using our shared helper from common.py
    log_path = get_challenge_file(root, CHALLENGE_ID, unlock)

    if not log_path.is_file():
        print(f"❌ ERROR: auth.log not found at {log_path}", file=sys.stderr)
        return False

    matches = scan_for_flags(log_path, REGEX_PATTERN)
    
    # Check if the expected flag appears in any of the matches
    if expected_flag in "\n".join(matches):
        print(f"✅ Validation success: found flag {expected_flag}")
        return True
    else:
        print(f"❌ Validation failed: flag {expected_flag} not found in auth.log.", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)