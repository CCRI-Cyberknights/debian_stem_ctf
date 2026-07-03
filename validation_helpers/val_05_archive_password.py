#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "05_ArchivePassword"

def check_dependencies():
    """Fail-fast check for required CLI tools."""
    for tool in ["unzip", "base64"]:
        if not shutil.which(tool):
            print(f"❌ ERROR: '{tool}' is not installed.", file=sys.stderr)
            sys.exit(1)

def unzip_with_password(zip_path: Path, password: str, extract_dir: Path) -> bool:
    """Extracts zip archive using provided password."""
    try:
        subprocess.run(
            ["unzip", "-o", "-P", password, str(zip_path), "-d", str(extract_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def decode_base64(path: Path) -> str:
    """Decodes base64 file content."""
    try:
        result = subprocess.run(
            ["base64", "-d", str(path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    
    real_flag = unlock.get("real_flag")
    password = unlock.get("last_zip_password")

    if not real_flag or not password:
        print(f"❌ ERROR: Missing metadata for {CHALLENGE_ID}.", file=sys.stderr)
        return False

    check_dependencies()
    
    # Path resolution
    zip_path = get_challenge_file(root, CHALLENGE_ID, unlock)
    extract_dir = zip_path.parent
    encoded_file = extract_dir / "message_encoded.txt"

    if not zip_path.is_file():
        print(f"❌ Zip file missing at: {zip_path}", file=sys.stderr)
        return False

    try:
        # Extract
        if not unzip_with_password(zip_path, password, extract_dir):
            print(f"❌ Failed to unzip {zip_path.name} with password.", file=sys.stderr)
            return False
            
        if not encoded_file.exists():
            print("❌ Extracted file missing.", file=sys.stderr)
            return False

        # Decode
        decoded_data = decode_base64(encoded_file)
        
        if real_flag in decoded_data:
            print(f"✅ Validation success: found flag {real_flag}")
            return True
        else:
            print("❌ Validation failed: flag not found in decoded output.", file=sys.stderr)
            return False

    finally:
        # Cleanup temporary files (message_encoded.txt)
        encoded_file.unlink(missing_ok=True)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)