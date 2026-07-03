#!/usr/bin/env python3

import sys
import shutil
import subprocess
import os
from pathlib import Path
from common import find_project_root, load_unlock_data, get_ctf_mode

CHALLENGE_ID = "06_Hashcat"

def check_dependencies():
    """Ensure required CLI tools are available."""
    for tool in ["unzip", "base64"]:
        if not shutil.which(tool):
            print(f"❌ ERROR: '{tool}' is not installed.", file=sys.stderr)
            sys.exit(1)

def decode_base64(input_path: Path, output_path: Path):
    """Decodes a single base64 file."""
    try:
        result = subprocess.run(
            ["base64", "-d", str(input_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output_path.write_text(result.stdout, encoding="utf-8")
    except subprocess.CalledProcessError:
        pass

def flatten_directory(directory: Path):
    """Moves all files from subdirectories to the root directory."""
    for file_path in directory.rglob("*"):
        if file_path.is_file() and file_path.parent != directory:
            shutil.move(str(file_path), str(directory / file_path.name))

def validate() -> bool:
    check_dependencies()
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    
    real_flag = unlock.get("real_flag")
    hash_map = unlock.get("hash_password_zip_map")

    if not real_flag or not hash_map:
        print(f"❌ ERROR: Missing metadata for {CHALLENGE_ID}.", file=sys.stderr)
        return False

    # Path setup
    base_folder = "challenges_solo" if get_ctf_mode() == "solo" else "challenges"
    challenge_dir = root / base_folder / CHALLENGE_ID
    
    # Sandbox support
    if os.environ.get("CCRI_SANDBOX"):
        challenge_dir = Path(os.environ["CCRI_SANDBOX"])

    segments_dir = challenge_dir / "segments"
    extracted_dir = challenge_dir / "extracted"
    decoded_dir = challenge_dir / "decoded_segments"
    assembled_file = challenge_dir / "assembled_flag.txt"

    try:
        # Prepare
        for d in [extracted_dir, decoded_dir]:
            if d.exists(): shutil.rmtree(d)
            d.mkdir(parents=True, exist_ok=True)

        # Sort parts: part1.zip, part2.zip...
        zip_to_pw = {Path(v["zip_file"]).name: v["password"] for v in hash_map.values()}
        sorted_parts = sorted(zip_to_pw.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0]))))

        # Pipeline: Extract & Decode
        for zip_name, password in sorted_parts:
            zip_path = segments_dir / zip_name
            if not zip_path.is_file(): continue
            
            subprocess.run(["unzip", "-o", "-P", password, str(zip_path), "-d", str(extracted_dir)], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            flatten_directory(extracted_dir)
            
            for f in extracted_dir.iterdir():
                if f.name.startswith("encoded_"):
                    decode_base64(f, decoded_dir / f"decoded_{f.name}")

        # Assemble
        decoded_files = sorted(
            [f for f in decoded_dir.iterdir() if f.name.endswith(".txt")],
            key=lambda f: int(''.join(filter(str.isdigit, f.name)))
        )
        
        all_lines = [f.read_text(encoding="utf-8").splitlines() for f in decoded_files]
        candidate_flags = ["-".join([lines[i] for lines in all_lines if i < len(lines)]) for i in range(5)]

        if real_flag in candidate_flags:
            print(f"✅ Validation success: flag {real_flag} found")
            return True
        else:
            print(f"❌ Validation failed: flag not found", file=sys.stderr)
            return False

    finally:
        # Cleanup
        for d in [extracted_dir, decoded_dir]:
            if d.exists(): shutil.rmtree(d)
        assembled_file.unlink(missing_ok=True)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)