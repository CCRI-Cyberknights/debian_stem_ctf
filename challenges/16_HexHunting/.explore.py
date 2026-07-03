#!/usr/bin/env python3
import sys
import subprocess
import time
import re
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen, safe_input

# === Config ===
BINARY_NAME = "hex_flag.bin"
NOTES_NAME = "notes.txt"

# === Core Helpers ===
def extract_flag_candidates(binary_path: Path) -> list:
    """Scans the target binary file bytes for strings matching plausible flag architectures."""
    try:
        data = binary_path.read_bytes()

        # Match CCRI-AAAA-1111, XXXX-YYYY-1111, XXXX-1111-YYYY
        flag_pattern = re.compile(
            rb"(CCRI-[A-Z]{4}-\d{4})|([A-Z]{4}-[A-Z]{4}-\d{4})|([A-Z]{4}-\d{4}-[A-Z]{4})"
        )

        matches = []
        for match in flag_pattern.finditer(data):
            flag_bytes = match.group(0)
            try:
                flag_str = flag_bytes.decode("ascii")
                matches.append((match.start(), flag_str))
            except UnicodeDecodeError:
                continue

        return matches

    except Exception as e:
        print_error(f"Binary scan sequence failed: {e}")
        return []

def show_hex_context(binary_path: Path, offset: int, context: int = 64):
    """Generates a localized hex dump view around the target candidate byte location."""
    start = max(0, offset - 16)
    try:
        dd = subprocess.Popen(
            ["dd", f"if={str(binary_path)}", "bs=1", f"skip={start}", f"count={context}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        xxd = subprocess.Popen(["xxd"], stdin=dd.stdout)
        if dd.stdout:
            dd.stdout.close()
        xxd.wait()
    except Exception as e:
        print_error(f"Could not render targeted hex context view: {e}")

# === Main Flow ===
def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    binary_path = script_dir / BINARY_NAME
    notes_path = script_dir / NOTES_NAME

    # 2. Mission Briefing
    header("🔍 Hex Flag Hunter")
    
    print(f"📄 Target binary: {Colors.BOLD}{BINARY_NAME}{Colors.END}")
    print(f"🔧 Strategy: {Colors.BOLD}Static Analysis{Colors.END}\n")
    print(f"🎯 Goal: Locate the real flag (format: {Colors.GREEN}CCRI-AAAA-1111{Colors.END}).\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Concept:** Files are just sequences of bytes. Even inside compiled code,")
    print("                      text strings are often stored in plain text.")
    print("   ➤ **The Strategy:** Instead of running the file (which might be dangerous),")
    print("                        we will inspect its raw data.")
    print("   ➤ **The Tools:** We use 'xxd' (Hex Dumper) and 'strings' to extract text.\n")
    
    # 3. Safety Check
    if not binary_path.is_file():
        print_error(f"CRITICAL ERROR: Cannot locate target tracking object '{BINARY_NAME}'")
        print_info(f"Looking in: {script_dir.as_posix()}")
        pause("Press ENTER to exit...") 
        sys.exit(1)

    # Clean previous notes safely via Pathlib
    notes_path.unlink(missing_ok=True)

    require_input("Type 'scan' when you're ready to begin scanning the binary: ", "scan")
    
    # Tool Explanation
    header("🛠️ Behind the Scenes")
    print("This script automates finding strings in a binary.\n")
    print("In a real terminal, you would run commands like this:\n")
    print(f"   {Colors.GREEN}strings hex_flag.bin | grep 'CCRI'{Colors.END}\n")
    print("To simulate this, we will scan the raw bytes for anything that *looks* like a flag,")
    print("and then let you inspect a hex dump around each candidate to judge context.\n")
    
    require_input("Type 'start' to begin the scan: ", "start")

    print(f"\n{Colors.CYAN}🔎 Scanning binary for flag-like patterns...{Colors.END}")
    spinner("Scanning")
    
    flags = extract_flag_candidates(binary_path)

    if not flags:
        print_error("No flag-like patterns found in the inspected binary content.")
        pause("Press ENTER to exit...")
        sys.exit(1)

    print(f"\n{Colors.GREEN}✅ Detected {len(flags)} flag-like pattern(s)!{Colors.END}")
    print("🧪 You'll now investigate each one by reviewing its raw hex context.")
    print("   Use what you know about the story + placement to decide what's real.")
    
    require_input("🔬 Type 'view' to begin reviewing candidates: ", "view")

    # 4. Review Loop
    for i, (offset, flag) in enumerate(flags):
        clear_screen()
        print("-" * 50)
        print(f"[{i+1}/{len(flags)}] 🏷️  Candidate Flag: {Colors.BOLD}{flag}{Colors.END}")
        print(f"📍 Approximate Byte Offset: {Colors.YELLOW}{offset}{Colors.END}")
        print("📖 Hex Dump Around Candidate:")
        print("-" * 50)
        
        print(Colors.CYAN)
        show_hex_context(binary_path, offset)
        print(Colors.END)
        print("-" * 50)

        while True:
            print("\nActions:")
            print(f"  [1] ✅ Mark as {Colors.GREEN}POSSIBLE{Colors.END} (save to {NOTES_NAME})")
            print("  [2] ➡️  Skip to next candidate")
            print("  [3] 🚪 Quit investigation")
            
            # Replaced raw input call with standard safe_input wrapper functionality
            choice = safe_input(f"{Colors.YELLOW}Choose an action (1-3): {Colors.END}").strip()
            
            if choice == "1":
                try:
                    with notes_path.open("a", encoding="utf-8") as f:
                        f.write(flag + "\n")
                    print_success(f"Saved '{flag}' to {NOTES_NAME}")
                except Exception as e:
                    print_error(f"Failed to append candidate entry to target notes artifact: {e}")
                time.sleep(0.6)
                break
            elif choice == "2":
                print_info("Skipping to next candidate...")
                time.sleep(0.4)
                break
            elif choice == "3":
                print(f"\n{Colors.CYAN}👋 Exiting early. Your saved flags are in {NOTES_NAME}.{Colors.END}")
                sys.exit(0)
            else:
                print_error("Invalid input specification parameter. Please enter 1, 2, or 3.")

    # 5. Conclusion
    print("\n")
    print_success("Flag inspection complete!")
    print(f"📁 Review your notes: {Colors.BOLD}{NOTES_NAME}{Colors.END}")
    print(f"{Colors.CYAN}🧠 Remember: Only one of those candidates is the true CCRI flag.{Colors.END}")
    pause("🔚 Press ENTER to exit.")

if __name__ == "__main__":
    main()