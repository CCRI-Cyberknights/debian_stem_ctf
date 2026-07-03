#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, safe_input

# === Config ===
IMAGE_FILE = "squirrel.jpg"
OUTPUT_FILE = "decoded_message.txt"

def run_steghide(password, image_path: Path, output_path: Path) -> bool:
    """Attempt to extract hidden file using steghide and given password."""
    try:
        result = subprocess.run(
            ["steghide", "extract", "-sf", str(image_path), "-xf", str(output_path), "-p", password, "-f"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Verify file state using Pathlib traits natively
        return result.returncode == 0 and output_path.is_file() and output_path.stat().st_size > 0
    except FileNotFoundError:
        print_error("steghide is not installed on this system.")
        return False

def main():
    # 1. Title Screen
    header("🕵️ Stego Decode Helper")
    
    print(f"🎯 Target: {Colors.BOLD}{IMAGE_FILE}{Colors.END}")
    print(f"🔍 Tool: {Colors.BOLD}steghide{Colors.END}\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ The target file is locked with a passphrase.")
    print("   ➤ Rumor has it the user used the \"most common password in the world.\"")
    print("   ➤ Your goal: Guess the password to unlock the file.\n")
    
    require_input("Type 'ready' when you are ready to start the extraction tool: ", "ready")

    # 2. Explainer Screen
    header("🛠️ Behind the Scenes")
    print("When you enter a password, this script runs the following Linux command:\n")
    print(f"   {Colors.GREEN}steghide extract -sf {IMAGE_FILE} -xf {OUTPUT_FILE} -p [PASSWORD]{Colors.END}\n")
    print("🔍 Command breakdown:")
    print(f"   {Colors.BOLD}steghide{Colors.END}          → The steganography tool")
    print(f"   {Colors.BOLD}extract{Colors.END}           → The action (pull data OUT)")
    print(f"   {Colors.BOLD}-sf {IMAGE_FILE}{Colors.END}  → Source File (the image)")
    print(f"   {Colors.BOLD}-xf {OUTPUT_FILE}{Colors.END} → Extract File (where to save the result)")
    print(f"   {Colors.BOLD}-p [PASSWORD]{Colors.END}     → The key to unlock the data\n")
    
    require_input("Type 'go' when you are ready to guess the password: ", "go")

    script_dir = Path(__file__).resolve().parent
    image_path = script_dir / IMAGE_FILE
    output_path = script_dir / OUTPUT_FILE

    # 3. Main Logic Loop
    while True:
        # Utilize unified safe_input to absorb manual abort shortcuts
        pw = safe_input(f"{Colors.YELLOW}🔑 Enter a password guess (or 'exit'): {Colors.END}").strip()
        
        if not pw:
            continue
            
        if pw.lower() == "exit":
            print(f"{Colors.CYAN}👋 Exiting.{Colors.END}")
            pause("Press ENTER to close this terminal...")
            break

        print(f"\n🔓 Attempting unlock with: {Colors.BOLD}{pw}{Colors.END}")
        spinner("Running steghide")

        if run_steghide(pw, image_path, output_path):
            print("\n" + "=" * 50)
            print_success("ACCESS GRANTED! Message recovered:")
            print("=" * 50)
            print("--------------- CONTENT ---------------")
            try:
                content = output_path.read_text(encoding="utf-8", errors="replace").strip()
                print(f"{Colors.BOLD}{content}{Colors.END}")
            except Exception as e:
                print_error(f"Failed to read recovered text file: {e}")
            print("---------------------------------------\n")
            print(f"📁 Evidence saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}")
            print(f"{Colors.CYAN}🧠 Look for the flag format: CCRI-AAAA-1111{Colors.END}")
            pause("Press ENTER to close this terminal...")
            break
        else:
            print_error("Access Denied. That password was incorrect.")
            print("💡 Hint: Search Google for 'most common passwords'.\n")
            # Clear invalid extraction artifacts safely via standard unlink rules
            output_path.unlink(missing_ok=True)