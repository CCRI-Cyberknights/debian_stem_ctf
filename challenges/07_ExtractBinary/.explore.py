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
BINARY_FILE = "hidden_flag"
STRINGS_FILE = "extracted_strings.txt"
REGEX_PATTERN = r'CCRI-[A-Z0-9]{4}-\d{4}'

def run_strings(binary_path: Path, output_path: Path):
    """Runs the system utility to drop readable text sequences into target file paths."""
    try:
        with output_path.open("w", encoding="utf-8", errors="ignore") as out_f:
            subprocess.run(["strings", str(binary_path)], stdout=out_f, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Failed to execute standard system 'strings' analysis diagnostic binary.")
        sys.exit(1)

def search_for_flags(file_path: Path, regex: str) -> list:
    """Scans file streams line-by-line using regular expressions to isolate matching structures."""
    matches = []
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                found = re.findall(regex, line)
                for flag in found:
                    matches.append(flag)
    except Exception as e:
        print_error(f"Error encountered during automated flag regular expression processing search: {e}")
        sys.exit(1)
    return matches

def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    binary_path = script_dir / BINARY_FILE
    strings_path = script_dir / STRINGS_FILE

    if not binary_path.is_file():
        print_error(f"The forensic analysis target executable file '{BINARY_FILE}' was not found.")
        sys.exit(1)

    # 2. Mission Briefing
    header("🧪 Binary Forensics Challenge")
    
    print(f"📦 Target binary: {Colors.BOLD}{BINARY_FILE}{Colors.END}")
    print(f"🔧 Tool in use: {Colors.BOLD}strings{Colors.END}\n")
    print("🎯 Goal: Uncover a hidden flag embedded inside this compiled program.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Lock:** The file is a binary executable (not readable text).")
    print("   ➤ **The Strategy:** Static Analysis (reading the raw data bytes).")
    print("   ➤ **The Tool:** The `strings` command pulls readable text out of binary noise.\n")
    
    require_input("Type 'ready' when you're ready to see the command we'll run: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("To extract all readable strings from the binary, we use:\n")
    print(f"   {Colors.GREEN}strings {BINARY_FILE} > {STRINGS_FILE}{Colors.END}\n")
    print("🔍 Command breakdown:")
    print(f"   {Colors.BOLD}strings {BINARY_FILE}{Colors.END}   → Scan the binary for printable text")
    print(f"   {Colors.BOLD}> {STRINGS_FILE:<20}{Colors.END}→ Redirect all found strings into a text file")
    print("\nAfter that, we can search inside the text file using tools like 'grep'.\n")
    
    require_input("Type 'run' when you're ready to extract strings from the binary: ", "run")

    print(f"\n🔍 Running: strings \"{BINARY_FILE}\" > \"{STRINGS_FILE}\"")
    spinner("Extracting strings")
    run_strings(binary_path, strings_path)
    time.sleep(0.3)
    print_success(f"All extracted strings saved to: {STRINGS_FILE}\n")

    print("📄 Previewing the first 15 lines of extracted text:")
    print("-" * 50)
    try:
        with strings_path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 15: 
                    break
                print(f"{Colors.YELLOW}{line.strip()}{Colors.END}")
    except FileNotFoundError:
        print_error(f"Could not open extracted storage baseline {STRINGS_FILE}.")
    print("-" * 50 + "\n")

    # 4. Keyword Search
    require_input("Type 'search' to enter a keyword search mode: ", "search")
    
    print(f"We know the flag starts with '{Colors.BOLD}CCRI{Colors.END}'.")
    keyword = safe_input(f"{Colors.YELLOW}🔍 Enter a keyword to search (or hit ENTER to use 'CCRI'): {Colors.END}").strip()
    
    if not keyword:
        keyword = "CCRI"
    
    print(f"\n🔎 Searching for '{Colors.BOLD}{keyword}{Colors.END}' in {STRINGS_FILE}...\n")
    
    print("   Command being used under the hood:")
    print(f"      {Colors.GREEN}grep {keyword} {STRINGS_FILE}{Colors.END}\n")
    time.sleep(0.5)
    
    try:
        # Pass path objects stringified securely to native subprocess arguments
        subprocess.run(["grep", "--color=always", keyword, str(strings_path)], check=False)
    except FileNotFoundError:
        print_error("System utility grep command was not discovered on the active host profile.")
        
    print("\n")
    print(f"{Colors.CYAN}🧠 Hint: If you see the flag above, copy it!{Colors.END}")
    print("   Format: CCRI-AAAA-1111\n")

    # 5. Automated Scan
    matches = search_for_flags(strings_path, REGEX_PATTERN)
    if matches:
        print(f"{Colors.GREEN}📌 Automated Scan confirmed {len(matches)} flag(s):{Colors.END}")
        for m in matches:
            print(f"   ➡️ {Colors.BOLD}{m}{Colors.END}")
    
    pause("\nPress ENTER to close this terminal...")

if __name__ == "__main__":
    main()