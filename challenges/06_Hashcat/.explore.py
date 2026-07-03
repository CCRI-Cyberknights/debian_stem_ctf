#!/usr/bin/env python3
import subprocess
import base64
import sys
import time
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen, safe_input

# === Config ===
HASHES_FILE = "hashes.txt"
WORDLIST_FILE = "wordlist.txt"
POTFILE = "hashcat.potfile"
SEGMENTS_DIR = "segments"
ASSEMBLED_FILE = "flag.txt"

def run_hashcat(hashes_path: Path, wordlist_path: Path, potfile_path: Path):
    """Executes hashcat tool to break the targeted hashes list."""
    subprocess.run(
        [
            "hashcat", "-m", "0", "-a", "0",
            str(hashes_path), str(wordlist_path),
            "--potfile-path", str(potfile_path), "--force"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def internal_assembly_logic() -> list:
    """
    Reads the extracted files, decodes them, and merges them in memory.
    Returns a list of assembled flag strings.
    """
    parts = ["encoded_segments1.txt", "encoded_segments2.txt", "encoded_segments3.txt"]
    decoded_columns = []

    # 1. Read and Decode each part securely via Pathlib
    for p in parts:
        part_path = Path.cwd() / p
        if not part_path.is_file():
            return []
        
        try:
            raw_data = part_path.read_bytes().strip()
            # Decode Base64 securely in memory
            decoded_text = base64.b64decode(raw_data).decode('utf-8')
            decoded_columns.append(decoded_text.splitlines())
        except Exception:
            return []

    # 2. Stitch data columns together systematically
    results = []
    if decoded_columns:
        # Verify alignment using the baseline row count from the first column
        num_rows = len(decoded_columns[0])
        for i in range(num_rows):
            row_pieces = []
            for col in decoded_columns:
                if i < len(col):
                    row_pieces.append(col[i].strip())
                else:
                    row_pieces.append("???")
            results.append("-".join(row_pieces))
            
    return results

def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    hashes_path = script_dir / HASHES_FILE
    wordlist_path = script_dir / WORDLIST_FILE
    potfile_path = script_dir / POTFILE
    segments_path = script_dir / SEGMENTS_DIR
    assembled_path = script_dir / ASSEMBLED_FILE

    # 2. Mission Briefing
    header("🔓 ZIP Hashcat ChainCrack Demo")
    
    print(f"📂 Hashes to crack:      {Colors.BOLD}{HASHES_FILE}{Colors.END}")
    print(f"📦 Encrypted segments:   {Colors.BOLD}segments/part*.zip{Colors.END}\n")
    print("🎯 Goal: Crack hashes, unlock ZIPs, and assemble the hidden flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Lock:** Three separate ZIP files, locked with different passwords.")
    print("   ➤ **The Keys:** Passwords hidden behind MD5 hashes.")
    print("   ➤ **The Strategy:** Crack -> Unlock -> Assemble.")
    print("   ➤ **The Requirement:** You must chain multiple tools together.\n")
    
    require_input("Type 'ready' to initialize the attack chain: ", "ready")

    if not hashes_path.is_file() or not wordlist_path.is_file():
        print_error("Required files hashes.txt or wordlist.txt are missing.")
        sys.exit(1)

    # 3. Algorithm Explanation
    header("🛠️ Behind the Scenes")
    print("This script simulates a complex automation pipeline:\n")
    
    print("1. **Crack**: It calls `hashcat` to recover the passwords from MD5 hashes.")
    print("2. **Unlock**: It uses those passwords to `unzip` the archive segments.")
    print("3. **Assemble**: It runs an internal algorithm to stitch the files.")
    
    print(f"\n{Colors.CYAN}🧩 The Assembly Logic:{Colors.END}")
    print("   The zips contain fragments of data. Manually pasting them together is slow.")
    print("   This script will load all three text files into memory, decode them from")
    print("   Base64, and align them line-by-line to reconstruct the flag.\n")
    
    require_input("Type 'start' to begin the chain reaction: ", "start")

    # 4. Execution Phase - Step 1: Crack
    # Clean previous run state safely
    potfile_path.unlink(missing_ok=True)
    
    print(f"\n{Colors.CYAN}🔨 [Phase 1] Cracking Hashes...{Colors.END}")
    spinner("Running Hashcat")
    run_hashcat(hashes_path, wordlist_path, potfile_path)

    # Map hashes to passwords
    cracked_map = {}
    if potfile_path.is_file():
        try:
            with open(potfile_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if ":" in line:
                        h, p = line.strip().split(":", 1)
                        cracked_map[h] = p
        except Exception as e:
            print_error(f"Failed to scan potfile database output: {e}")
            sys.exit(1)
    else:
        print_error("Hashcat execution dropped without creating a potfile record map.")
        sys.exit(1)

    # Get ordered passwords based on hashes.txt tracking order
    ordered_passwords = []
    try:
        with open(hashes_path, "r", encoding="utf-8") as f:
            for line in f:
                h = line.strip()
                if h: 
                    ordered_passwords.append(cracked_map.get(h))
    except Exception as e:
        print_error(f"Failed to index master hash manifest sequence: {e}")
        sys.exit(1)
            
    print_success("Hashes cracked successfully.")
    for i, pw in enumerate(ordered_passwords):
        print(f"   Hashes #{i+1} -> Password: {Colors.BOLD}{pw}{Colors.END}")
    
    time.sleep(1)

    # 5. Execution Phase - Step 2: Unlock
    print(f"\n{Colors.CYAN}🔓 [Phase 2] Unlocking Archives...{Colors.END}")
    
    # Purge historical tracking files from the local directory context via clean iterator
    for item in Path.cwd().iterdir():
        if item.is_file() and item.name.startswith("encoded_segments"):
            item.unlink()

    for i, pw in enumerate(ordered_passwords):
        if not pw:
            print_error(f"   Skipping Part {i+1} (Target plain text password unknown)")
            continue
            
        zip_file = segments_path / f"part{i+1}.zip"
        print(f"   Unzipping {zip_file.name} with key '{pw}'...", end="")
        
        res = subprocess.run(
            ["unzip", "-o", "-P", pw, str(zip_file)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        if res.returncode == 0:
            print(f" {Colors.GREEN}OK{Colors.END}")
        else:
            print(f" {Colors.RED}FAILED{Colors.END}")
            
    time.sleep(1)

    # 6. Execution Phase - Step 3: Assemble (Internal)
    print(f"\n{Colors.CYAN}🧩 [Phase 3] Assembling Fragments (Internal Logic)...{Colors.END}")
    spinner("Processing in memory")
    
    candidate_flags = internal_assembly_logic()
    
    if not candidate_flags:
        print_error("Assembly failed. Are the extracted segment files corrupted or missing?")
    else:
        # Commit aligned output back to disk tracking arrays
        try:
            assembled_path.write_text("\n".join(candidate_flags) + "\n", encoding="utf-8")
            print_success("Data fragment assembly process completed.")
            print("-" * 40)
            for flag in candidate_flags:
                print(f"{Colors.BOLD}{flag}{Colors.END}")
            print("-" * 40 + "\n")
            
            print(f"✅ Flags saved to: {Colors.BOLD}{ASSEMBLED_FILE}{Colors.END}")
            print(f"{Colors.CYAN}🧠 Hint: Look for the one matching CCRI-AAAA-1111.{Colors.END}")
        except Exception as e:
            print_error(f"Failed to output completed flag arrays to tracking files: {e}")

    pause("\n🎉 Press ENTER to exit...")

if __name__ == "__main__":
    main()