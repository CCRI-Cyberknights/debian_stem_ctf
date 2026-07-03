#!/usr/bin/env python3

import sys
import subprocess
import shutil
from common import find_project_root, load_unlock_data

CHALLENGE_ID = "17_NmapScanning"

def check_dependencies():
    """Fail-fast check for required CLI tools."""
    if not shutil.which("curl"):
        print("❌ ERROR: 'curl' is not installed.", file=sys.stderr)
        sys.exit(1)

def fetch_port_response(port: int) -> str:
    """Attempts to fetch the response from the specific port."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "2", f"http://localhost:{port}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Curl connection failed: {e}", file=sys.stderr)
        return ""

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    
    expected_flag = unlock.get("real_flag")
    expected_port = unlock.get("real_port")

    if not expected_flag or not expected_port:
        print(f"❌ ERROR: Missing metadata (flag or port) for {CHALLENGE_ID}.", file=sys.stderr)
        return False

    check_dependencies()

    print(f"🔎 Validating port {expected_port} for expected flag...")
    response = fetch_port_response(int(expected_port))

    if expected_flag in response:
        print(f"✅ Validation success: found flag {expected_flag} on port {expected_port}")
        return True
    else:
        preview = (response[:100] + "...") if len(response) > 100 else response
        print(f"❌ Validation failed: flag {expected_flag} not found on port {expected_port}.", file=sys.stderr)
        print(f"   Response preview: {preview}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)