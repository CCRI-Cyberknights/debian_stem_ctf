#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "18_PcapSearch"

def check_dependencies():
    """Fail-fast check for required CLI tools."""
    for tool in ["tshark", "xxd"]:
        if not shutil.which(tool):
            print(f"❌ ERROR: '{tool}' is not installed.", file=sys.stderr)
            sys.exit(1)

def fast_search_flag(pcap: Path, flag: str) -> bool:
    """Uses a tshark pipeline to extract and search TCP payloads."""
    # Pipeline: tshark extracts hex payloads -> xxd converts hex to raw bytes -> strings searches for ASCII
    cmd = f"tshark -r {str(pcap)} -Y 'tcp' -T fields -e tcp.payload | xxd -r -p | strings"
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=True
        )
        return flag in result.stdout
    except subprocess.CalledProcessError:
        print("❌ ERROR: Tshark pipeline failed.", file=sys.stderr)
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
    # We locate the parent directory to find traffic.pcap
    base_file = get_challenge_file(root, CHALLENGE_ID, unlock)
    pcap_path = base_file.parent / "traffic.pcap"

    if not pcap_path.is_file():
        print(f"❌ ERROR: PCAP file missing at {pcap_path}", file=sys.stderr)
        return False

    if fast_search_flag(pcap_path, expected_flag):
        print(f"✅ Validation success: found flag '{expected_flag}' in PCAP.")
        return True
    
    print(f"❌ Validation failed: flag '{expected_flag}' NOT found in PCAP.", file=sys.stderr)
    return False

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)