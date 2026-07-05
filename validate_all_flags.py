#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path

# === Paths (Relative to this script) ===
BASE_DIR = Path(__file__).resolve().parent
CHALLENGES_JSON = BASE_DIR / "web_version_admin/challenges.json"
CHALLENGES_JSON_SOLO = BASE_DIR / "web_version_admin/challenges_solo.json"
UNLOCKS_GUIDED = BASE_DIR / "web_version_admin/validation_unlocks.json"
UNLOCKS_SOLO = BASE_DIR / "web_version_admin/validation_unlocks_solo.json"
VALIDATION_MODULES = BASE_DIR / "validation_helpers"
SANDBOX_ROOT = BASE_DIR / ".validation_sandbox"

# === Mapping: challenge_id -> validation_helpers/module.py ===
CHALLENGE_TO_MODULE = {
    "01_Stego": "val_01_stego",
    "02_Base64": "val_02_base64",
    "03_ROT13": "val_03_rot13",
    "04_Vigenere": "val_04_vigenere",
    "05_ArchivePassword": "val_05_archive_password",
    "06_Hashcat": "val_06_hashcat",
    "07_ExtractBinary": "val_07_extract_binary",
    "08_FakeAuthLog": "val_08_fake_auth_log",
    "09_FixScript": "val_09_fix_script",
    "10_Metadata": "val_10_metadata",
    "11_HiddenFlag": "val_11_hidden_flag",
    "12_QRCodes": "val_12_qr_codes",
    "13_HTTPHeaders": "val_13_http_headers",
    "14_InternalPortals": "val_14_internal_portals",
    "15_ProcessInspection": "val_15_process_inspection",
    "16_HexHunting": "val_16_hex_hunting",
    "17_NmapScanning": "val_17_nmap_scanning",
    "18_PcapSearch": "val_18_pcap_search"
}

def choose_mode():
    print("\n🎛️ Choose validation mode:")
    print("[1] Guided (default)")
    print("[2] Solo")
    choice = input("Enter choice [1/2]: ").strip()
    return "solo" if choice == "2" else "guided"

def load_challenge_list(mode):
    path = CHALLENGES_JSON_SOLO if mode == "solo" else CHALLENGES_JSON
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def run_validator(challenge_id, mode):
    module_name = CHALLENGE_TO_MODULE.get(challenge_id)
    if not module_name:
        print(f"⚠️  Skipped: No module mapping for {challenge_id}")
        return False

    script_path = VALIDATION_MODULES / f"{module_name}.py"
    print(f"\n🔍 Validating {challenge_id}...")

    if not script_path.exists():
        print(f"⚠️  Skipped: {script_path} not found.")
        return False

    # Define paths for this specific challenge's sandbox container
    challenge_sandbox = SANDBOX_ROOT / challenge_id
    
    # Ensure a clean staging directory exists
    if challenge_sandbox.exists():
        shutil.rmtree(challenge_sandbox)

    # Locate generated source data from the active build mode
    src_folder_name = "challenges_solo" if mode == "solo" else "challenges"
    source_assets_dir = BASE_DIR / src_folder_name / challenge_id

    # Populate the sandbox container with the challenge assets dynamically
    if source_assets_dir.is_dir():
        shutil.copytree(source_assets_dir, challenge_sandbox)
    else:
        challenge_sandbox.mkdir(parents=True, exist_ok=True)

    # Setup environment parameters for the isolated sub-process execution
    env = os.environ.copy()
    env["CCRI_MODE"] = mode
    env["CCRI_SANDBOX"] = str(challenge_sandbox)

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=VALIDATION_MODULES,
            env=env,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception running validator: {e}", file=sys.stderr)
        return False

def main():
    print("🚦 CCRI STEMDay Master Validator\n" + "=" * 40)
    
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else choose_mode()
    if mode not in ("guided", "solo"):
        print("❌ Invalid mode. Use: ./validate_all_flags.py [guided|solo]")
        sys.exit(1)

    # Prepare Workspace Root Environment
    if SANDBOX_ROOT.exists():
        shutil.rmtree(SANDBOX_ROOT)
    SANDBOX_ROOT.mkdir()

    print(f"🛠️ Mode: {mode.upper()}")
    challenges = load_challenge_list(mode)

    success_count = 0
    fail_count = 0

    for challenge_id in challenges:
        if run_validator(challenge_id, mode):
            success_count += 1
        else:
            fail_count += 1

    print("\n" + "=" * 40)
    print("📊 Validation Summary:")
    print(f"✅ {success_count} passed")
    print(f"❌ {fail_count} failed")
    
    if fail_count == 0:
        print("\n🎉 All challenges validated successfully!")
    else:
        print("\n🚨 Some challenges failed. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()