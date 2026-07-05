#!/usr/bin/env python3

import sys
import shutil
import subprocess
import os
from pathlib import Path
from common import find_project_root, load_unlock_data, get_ctf_mode

CHALLENGE_ID = "06_Hashcat"

def check_dependencies():
    """Ensure required core system CLI utilities are available on the host."""
    for tool in ["unzip", "base64"]:
        if not shutil.which(tool):
            print(f"❌ ERROR: '{tool}' is not currently installed on this system.", file=sys.stderr)
            sys.exit(1)

def decode_base64(input_path: Path, output_path: Path) -> bool:
    """Decodes an intercepted base64 text block using standard coreutils flags."""
    try:
        result = subprocess.run(
            ["base64", "-d", str(input_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        output_path.write_text(result.stdout, encoding="utf-8")
        return True
    except subprocess.CalledProcessError:
        return False

def flatten_directory(directory: Path):
    """Recursively walks the sandbox directory to normalize any nested archive assets."""
    for root, _, files in os.walk(directory):
        for f in files:
            src = Path(root) / f
            dst = directory / f
            if src != dst:
                if dst.exists():
                    dst.unlink()
                src.rename(dst)

def extract_and_decode(passwords: list, segments_dir: Path, extracted_dir: Path, decoded_dir: Path):
    """Sequentially extracts data partitions and decodes their payloads in-line."""
    extracted_dir.mkdir(exist_ok=True)
    decoded_dir.mkdir(exist_ok=True)

    for idx, password in enumerate(passwords, 1):
        zip_file = segments_dir / f"part{idx}.zip"
        if not zip_file.exists():
            print(f"⚠️  Missing challenge data segment: {zip_file}", file=sys.stderr)
            continue
            
        # Using the explicit overwrite flag ensures unzip never blocks waiting for stdin prompts
        subprocess.run(
            ["unzip", "-o", "-P", password, str(zip_file), "-d", str(extracted_dir)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        flatten_directory(extracted_dir)
        
        for f in extracted_dir.iterdir():
            if f.name.startswith("encoded_"):
                out_path = decoded_dir / f"decoded_{f.name}"
                decode_base64(f, out_path)

def assemble_flag(decoded_dir: Path, output_file: Path) -> list:
    """Transposes text lines across sorted data segments to rebuild the flag matrix."""
    decoded_files = sorted(
        [f for f in decoded_dir.iterdir() if f.name.endswith(".txt")],
        key=lambda f: int(''.join(filter(str.isdigit, f.name)))
    )
    lines_per_file = [f.read_text(encoding="utf-8").splitlines() for f in decoded_files]
    candidate_flags = []

    with output_file.open("w", encoding="utf-8") as f_out:
        for i in range(5):
            parts = [(lines[i] if i < len(lines) else "MISSING") for lines in lines_per_file]
            flag = "-".join(parts)
            candidate_flags.append(flag)
            f_out.write(flag + "\n")

    return candidate_flags

def validate(mode="guided", challenge_id=CHALLENGE_ID) -> bool:
    check_dependencies()
    root = find_project_root()
    data = load_unlock_data(root, challenge_id)
    flag = data.get("real_flag")
    
    hash_map = data.get("hash_password_zip_map")
    if not flag or not hash_map:
        print(f"❌ ERROR: Missing flag or configuration mapping inside unlock metadata maps.", file=sys.stderr)
        return False

    # Map tracking hashes back to their absolute password strings sorted cleanly by part number
    zip_to_password = {
        Path(entry["zip_file"]).name: entry["password"]
        for entry in hash_map.values()
    }
    sorted_parts = sorted(zip_to_password.items(), key=lambda x: int(''.join(filter(str.isdigit, x[0]))))
    passwords = [pw for _, pw in sorted_parts]

    sandbox_override = os.environ.get("CCRI_SANDBOX")
    if sandbox_override:
        challenge_dir = Path(sandbox_override)
    else:
        base_path = "challenges_solo" if mode == "solo" else "challenges"
        challenge_dir = root / base_path / challenge_id

    segments = challenge_dir / "segments"
    extracted = challenge_dir / "extracted"
    decoded = challenge_dir / "decoded_segments"
    assembled = challenge_dir / "assembled_flag.txt"

    # Reset local testing workspace folders cleanly
    for d in [extracted, decoded]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    # Execute processing pipelines
    extract_and_decode(passwords, segments, extracted, decoded)
    flags = assemble_flag(decoded, assembled)

    if flag in flags:
        print(f"✅ Validation success: flag {flag} found")
        return True
    else:
        print(f"❌ Validation failed: flag {flag} not found within reconstructed segments.", file=sys.stderr)
        return False

if __name__ == "__main__":
    from common import get_ctf_mode
    mode = get_ctf_mode()
    success = validate(mode=mode)
    sys.exit(0 if success else 1)