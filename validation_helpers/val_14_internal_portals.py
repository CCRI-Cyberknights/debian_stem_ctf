#!/usr/bin/env python3

import sys
import json
import base64
import re
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "14_InternalPortals"

def validate_server_data(server_data_file: Path, expected_flag: str) -> bool:
    """Decodes the server data blob and inspects HTML for the flag."""
    if not server_data_file.exists():
        print(f"❌ ERROR: File missing: {server_data_file}", file=sys.stderr)
        return False

    try:
        b64_content = server_data_file.read_text(encoding="utf-8").strip()
        json_str = base64.b64decode(b64_content).decode("utf-8")
        data_map = json.loads(json_str)
        print(f"✅ Decoded {len(data_map)} portals.")
    except Exception as e:
        print(f"❌ ERROR: Decode failed: {e}", file=sys.stderr)
        return False

    found_flags = []
    
    # Check portals for the specific hidden span
    for site, html in data_map.items():
        if "id='debug-info'" in html or 'id="debug-info"' in html:
            if expected_flag in html:
                print(f"✅ SUCCESS! Exact flag found in hidden span on '{site}'")
                return True

        # Fallback: check for standard flag pattern
        flag_pattern = re.compile(r"CCRI-[A-Z0-9]{4}-\d{4}")
        matches = flag_pattern.findall(html)
        for m in matches:
            found_flags.append(f"{site}: {m}")

    print(f"\n❌ FAILURE: Expected flag {expected_flag} NOT found in any portal.", file=sys.stderr)
    
    if found_flags:
        print("⚠️ Detected flag-like strings, but none matched the target:")
        for f in found_flags:
            print(f"   - {f}")
    
    return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Path resolution using shared helper
    # We locate the parent directory of the challenge file to find .server_data
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    server_data_file = base_file.parent / ".server_data"

    return validate_server_data(server_data_file, expected_flag)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)