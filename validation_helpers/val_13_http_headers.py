#!/usr/bin/env python3

import sys
import json
import base64
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "13_HTTPHeaders"

def validate_server_data(challenge_dir: Path, expected_flag: str) -> bool:
    """Decodes hidden server config and checks for the X-Flag header."""
    data_file = challenge_dir / ".server_data"
    
    if not data_file.exists():
        print(f"❌ Missing challenge data file: {data_file}", file=sys.stderr)
        return False

    try:
        # Read and decode the hidden server configuration
        encoded_content = data_file.read_text(encoding="utf-8").strip()
        decoded_json = base64.b64decode(encoded_content).decode('utf-8')
        data_map = json.loads(decoded_json)

        # Iterate through all generated endpoints
        for endpoint_name, endpoint_data in data_map.items():
            headers = endpoint_data.get("headers", {})
            
            # Check the specific header where we hide the flag
            if headers.get("X-Flag") == expected_flag:
                print(f"✅ Validation success: found correct flag in {endpoint_name} headers.")
                return True

        print(f"❌ Validation failed: flag {expected_flag} not found in any endpoint configuration.", file=sys.stderr)
        return False

    except Exception as e:
        print(f"❌ Error parsing server data: {e}", file=sys.stderr)
        return False

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    expected_flag = unlock.get("real_flag")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Path resolution using shared helper
    # We need the parent directory of the challenge file to find '.server_data'
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    challenge_dir = base_file.parent

    return validate_server_data(challenge_dir, expected_flag)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)