#!/usr/bin/env python3

import sys
import subprocess
import shutil
import re
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "07_ExtractBinary"
# CCRI-XXXX-XXXX format
REGEX_PATTERN = r'\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b'

def check_dependencies():
    """Fail-fast check for required CLI tools."""
    if not shutil.which("strings"):
        print("❌ ERROR: 'strings' is not installed.", file=sys.stderr)
        sys.exit(1)

def run_strings(binary_path: Path, output_path: Path) -> bool:
    """Extracts strings from the binary."""
    try:
        with output_path.open("w", encoding="utf-8") as out_f:
            subprocess.run(["strings", str(binary_path)], stdout=out_f, check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ ERROR: Failed to run 'strings'.", file=sys.stderr)
        return False

def search_for_flags(file_path: Path, pattern: str) -> list[str]:
    """Searches extracted strings for the flag pattern."""
    matches = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        matches = re.findall(pattern, content)
    except Exception as e:
        print(f"❌ ERROR during flag search: {e}", file=sys.stderr)
    return matches

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    check_dependencies()

    # Get path using our shared helper
    binary_path = get_challenge_file(root, CHALLENGE_ID, unlock)
    extracted_path = binary_path.parent / "extracted_strings.txt"

    if not binary_path.is_file():
        print(f"❌ ERROR: Binary file not found at {binary_path}", file=sys.stderr)
        return False

    try:
        if not run_strings(binary_path, extracted_path):
            return False

        matches = search_for_flags(extracted_path, REGEX_PATTERN)
        
        if expected_flag in matches:
            print(f"✅ Validation success: found flag {expected_flag}")
            return True
        else:
            print(f"❌ Validation failed: flag {expected_flag} not found in extracted strings.", file=sys.stderr)
            return False

    finally:
        # Cleanup temporary artifact
        extracted_path.unlink(missing_ok=True)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)