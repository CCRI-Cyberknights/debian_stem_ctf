#!/usr/bin/env python3
import subprocess
import sys
import time
import re
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen, safe_input

# === Config ===
IMAGE_FILE = "capybara.jpg"
OUTPUT_FILE = "metadata_dump.txt"

def extract_flag_candidates(text: str) -> list:
    """Extract and display unique plausible flag-like values from metadata text streams."""
    pattern = r"CCRI-[A-Z0-9]{4}-[0-9]{4}"
    matches = re.findall(pattern, text)
    return list(set(matches))

def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    target_image = script_dir / IMAGE_FILE
    output_path = script_dir / OUTPUT_FILE

    if not target_image.is_file():
        print_error(f"{IMAGE_FILE} not discovered in the targeted workspace path context.")
        sys.exit(1)

    # 2. Mission Briefing
    header("📷 Metadata Inspection Tool")
    
    print(f"🎯 Target image: {Colors.BOLD}{IMAGE_FILE}{Colors.END}")
    print(f"🔧 Tool in use: {Colors.BOLD}exiftool{Colors.END}\n")
    print("🎯 Goal: Extract hidden metadata from the image to find the flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Lock:** Information is hidden in file headers (EXIF tags).")
    print("   ➤ **The Strategy:** Metadata Extraction (reading data about data).")
    print("   ➤ **The Tool:** `exiftool` is the industry standard for this task.\n")
    
    require_input("Type 'ready' to inspect the image headers: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("To inspect metadata, we'll use exiftool like this:\n")
    print(f"   {Colors.GREEN}exiftool {IMAGE_FILE} > {OUTPUT_FILE}{Colors.END}\n")
    print("🔍 Command breakdown:")
    print(f"   {Colors.BOLD}exiftool {IMAGE_FILE}{Colors.END}        → Print all metadata fields for this image")
    print(f"   {Colors.BOLD}> {OUTPUT_FILE:<22}{Colors.END}→ Redirect the output into a text file to review later\n")
    print("Once we have metadata_dump.txt, we can:")
    print("   ➤ Skim fields (comments, artist, GPS, etc.)")
    print("   ➤ Search for keywords using `grep` (like 'CCRI')\n")
    
    require_input("Type 'run' when you're ready to extract metadata: ", "run")

    # 4. Execution
    print(f"\n📂 Inspecting: {Colors.BOLD}{IMAGE_FILE}{Colors.END}")
    print(f"📄 Saving output to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}\n")
    print(f"🛠️ Running: exiftool {IMAGE_FILE} > {OUTPUT_FILE}")
    spinner("Extracting metadata")

    try:
        with output_path.open("w", encoding="utf-8", errors="replace") as out_f:
            subprocess.run(
                ["exiftool", str(target_image)],
                stdout=out_f,
                stderr=subprocess.DEVNULL,
                check=True
            )
    except subprocess.CalledProcessError:
        print_error("exiftool runtime instance execution dropped with non-zero exit state.")
        sys.exit(1)
    except FileNotFoundError:
        print_error("exiftool utility binary context was not located on the host profile server.")
        sys.exit(1)

    print_success("Metadata extraction complete.\n")

    # 5. Preview & Filter
    print("👀 Let’s preview the first few lines of the dump:")
    print("-" * 50)
    try:
        metadata_text = output_path.read_text(encoding="utf-8", errors="replace")
        lines = metadata_text.splitlines()
        for line in lines[:10]:
            print(f"{Colors.YELLOW}{line}{Colors.END}")
    except Exception as e:
        print_error(f"Failed to scan metadata extraction dump: {e}")
    print("-" * 50 + "\n")

    require_input("Type 'filter' to search for the flag: ", "filter")
    
    # 6. Filtering (grep simulation)
    print(f"\n🔎 Searching for '{Colors.BOLD}CCRI{Colors.END}' in {OUTPUT_FILE}...\n")
    print("   Command being used under the hood:")
    print(f"      {Colors.GREEN}grep \"CCRI\" {OUTPUT_FILE}{Colors.END}\n")
    
    time.sleep(1)
    
    flag_candidates = extract_flag_candidates(metadata_text)
    
    if flag_candidates:
        print_success("Match found!")
        print("-" * 50)
        for flag in flag_candidates:
            print(f"   ➡️ {Colors.BOLD}{flag}{Colors.END}")
        print("-" * 50 + "\n")
        
        print(f"📁 Evidence saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}")
        print(f"{Colors.CYAN}🧠 This metadata field was hidden inside the file header.{Colors.END}\n")
    else:
        print_error("No flag format found in metadata fields.")
        print_info("Try inspecting the file manually or looking for other keywords.")

    pause("Press ENTER to close this terminal...")

if __name__ == "__main__":
    main()