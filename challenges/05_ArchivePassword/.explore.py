#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen, safe_input

# === Config ===
ZIP_FILE = "secret.zip"
WORDLIST = "wordlist.txt"
B64_FILE = "message_encoded.txt"
OUTPUT_FILE = "decoded_output.txt"

def progress_bar(length=30, delay=0.03):
    """Renders a simple visual loading bar sequence."""
    for _ in range(length):
        sys.stdout.write("█")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    zip_path = script_dir / ZIP_FILE
    wordlist_path = script_dir / WORDLIST
    b64_path = script_dir / B64_FILE
    output_path = script_dir / OUTPUT_FILE

    if not zip_path.is_file() or not wordlist_path.is_file():
        print_error("Missing zip file archiver target or verification wordlist configuration.")
        sys.exit(1)

    # 2. Mission Briefing
    header("🔓 ZIP Password Cracking Challenge")
    
    print(f"📄 Target Archive: {Colors.BOLD}{ZIP_FILE}{Colors.END}")
    print(f"📄 Password List:  {Colors.BOLD}{WORDLIST}{Colors.END}")
    print("🎯 Goal: Automate a dictionary attack to break the lock.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Lock:** Standard ZIP encryption.")
    print("   ➤ **The Strategy:** Dictionary Attack.")
    print("   ➤ **The Concept:** Trying every single word in a list until one works.")
    print("   ➤ **The Requirement:** Humans are too slow. We must use automation.\n")
    
    require_input("Type 'ready' to initialize the attack tools: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("This script simulates the automation required for a Dictionary Attack.")
    print("It effectively writes a loop that runs the following commands thousands of times:\n")
    
    print("Step 1: Test a password candidate (without extracting yet)")
    print(f"   {Colors.GREEN}unzip -P [PASSWORD] -t {ZIP_FILE}{Colors.END}\n")
    
    print("Step 2: If the test returns 'OK', extract the files")
    print(f"   {Colors.GREEN}unzip -o -P [PASSWORD] {ZIP_FILE} -d .{Colors.END}\n")
    
    print("Step 3: Decode the inner content (as seen in Challenge #2)")
    print(f"   {Colors.GREEN}base64 --decode {B64_FILE} > {OUTPUT_FILE}{Colors.END}\n")
    
    require_input("Type 'start' to launch the brute force attack: ", "start")

    # 4. Cracking Phase
    clear_screen()
    print(f"{Colors.CYAN}🔍 Beginning Dictionary Attack...{Colors.END}\n")
    print(f"📁 Wordlist: {Colors.BOLD}{WORDLIST}{Colors.END}")
    print(f"📦 Target:   {Colors.BOLD}{ZIP_FILE}{Colors.END}\n")
    print("⏳ Starting engine...\n")
    progress_bar(length=20, delay=0.04)

    found = False
    password = None

    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                pw = line.strip()
                if not pw: 
                    continue
                
                # Overwrite line dynamically for real-time tracking visualization
                print(f"\r[🔐] Testing: {Colors.YELLOW}{pw:<20}{Colors.END}", end="", flush=True)
                time.sleep(0.01)

                # Execute integrity test validation checks
                result = subprocess.run(
                    ["unzip", "-P", pw, "-t", str(zip_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if "OK" in result.stdout:
                    print(f"\n\n{Colors.GREEN}✅ MATCH FOUND: {Colors.BOLD}{pw}{Colors.END}")
                    password = pw
                    found = True
                    break
    except Exception as e:
        print_error(f"Error encountered during cracking session execution: {e}")
        sys.exit(1)

    if not found:
        print("\n")
        print_error("Password not found inside configured wordlist asset storage.")
        pause("Press ENTER to close this terminal...")
        sys.exit(1)

    # 5. Extraction Phase
    while True:
        proceed = safe_input(f"\n{Colors.YELLOW}📦 Extract and decode the message now? (yes/no): {Colors.END}").strip().lower()
        if proceed == "yes":
            break
        elif proceed == "no":
            print(f"\n{Colors.CYAN}👋 Exiting without extracting.{Colors.END}")
            pause("Press ENTER to close this terminal...")
            return
        else:
            print(f"{Colors.RED}   ❌ Please type 'yes' or 'no'.{Colors.END}")

    print("\n📦 Extracting archive contents...\n")
    spinner("Extracting files")

    subprocess.run(
        ["unzip", "-o", "-P", password, str(zip_path), "-d", str(script_dir)],
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

    if not b64_path.is_file():
        print_error("Extraction failed: missing Base64 payload storage reference target.")
        pause("Press ENTER to close this terminal...")
        sys.exit(1)

    clear_screen()
    print(f"📄 Extracted Base64 Message ({B64_FILE}):")
    print("-" * 50)
    try:
        b64_content = b64_path.read_text(encoding="utf-8", errors="replace")
        print(f"{Colors.YELLOW}{b64_content}{Colors.END}")
    except Exception as e:
        print_error(f"Failed to read payload extraction output: {e}")
    print("-" * 50 + "\n")

    # 6. Decoding Phase
    while True:
        decode = safe_input(f"{Colors.YELLOW}🔎 Decode the message now? (yes/no): {Colors.END}").strip().lower()
        if decode == "yes":
            break
        elif decode == "no":
            print(f"\n{Colors.CYAN}👋 Exiting without decoding.{Colors.END}")
            pause("Press ENTER to close this terminal...")
            return
        else:
            print(f"{Colors.RED}   ❌ Please type 'yes' or 'no'.{Colors.END}\n")

    print("\n⏳ Decoding message with Base64...\n")
    progress_bar(length=25, delay=0.03)

    result = subprocess.run(
        ["base64", "--decode", str(b64_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        print_error("Base64 stream translation processing failed.")
        pause("Press ENTER to close this terminal...")
        sys.exit(1)

    decoded = result.stdout.strip()
    try:
        output_path.write_text(decoded + "\n", encoding="utf-8")
    except Exception as e:
        print_error(f"Failed to commit cleartext flag matrix onto disk tracking arrays: {e}")

    # 7. Final Success
    print(f"\n{Colors.GREEN}🧾 Decoded Message:{Colors.END}")
    print("-" * 50)
    print(f"{Colors.BOLD}{decoded}{Colors.END}")
    print("-" * 50 + "\n")
    print(f"💾 Saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}")
    print(f"{Colors.CYAN}🧠 Look for a flag like: CCRI-AAAA-1111{Colors.END}\n")
    
    pause("Press ENTER to close this terminal...")

if __name__ == "__main__":
    main()