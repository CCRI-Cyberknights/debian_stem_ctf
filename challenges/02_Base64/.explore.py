#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, safe_input

# === Config ===
INPUT_FILE = "encoded.txt"
OUTPUT_FILE = "decoded_output.txt"

def decode_base64(input_path: Path, output_path: Path):
    """Decode a Base64-encoded file using the system tool and save the result."""
    try:
        result = subprocess.run(
            ["base64", "--decode", str(input_path)],
            capture_output=True,
            text=True,
            check=True
        )
        decoded = result.stdout.strip()
        if decoded:
            output_path.write_text(decoded + "\n", encoding="utf-8")
        return decoded
    except subprocess.CalledProcessError:
        return None
    except FileNotFoundError:
        return None

# === Main Flow ===
def main():
    # 1. Mission Briefing
    header("📡 Intercepted Transmission Decoder")
    
    print(f"📄 Target File: {Colors.BOLD}{INPUT_FILE}{Colors.END}")
    print("🎯 Goal: Decode the transmission to retrieve the flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ Base64 is NOT encryption; it is an encoding scheme.")
    print("   ➤ **The Signature:** Look for random text ending in `=` or `==`.")
    print("   ➤ **The Tool:** We will use the Linux `base64` utility to reverse it.\n")

    require_input("Type 'ready' when you're ready to inspect the evidence: ", "ready")

    # 2. File Inspection
    header("🔍 Step 1: Verification")
    script_dir = Path(__file__).resolve().parent
    input_path = script_dir / INPUT_FILE
    output_path = script_dir / OUTPUT_FILE
    
    print(f"Let's check if the file matches the Base64 signature described in the intel.\n")
    spinner("Reading file")
    print("\n")

    print(f"📄 Content of {INPUT_FILE}:")
    print("-" * 50)
    try:
        content = input_path.read_text(encoding="utf-8", errors="replace").strip()
        print(f"{Colors.YELLOW}{content}{Colors.END}")
    except FileNotFoundError:
        print_error(f"{INPUT_FILE} not found!")
        pause()
        return
    print("-" * 50 + "\n")
    
    if content.endswith("="):
        print(f"✅ {Colors.GREEN}Signature Confirmed:{Colors.END} The file ends with padding (`=`).")
        print("This confirms it is likely Base64 encoded.\n")
    else:
        print(f"⚠️ {Colors.YELLOW}Note:{Colors.END} No padding visible, but valid Base64 doesn't always need it.")
        print("We will proceed with the decode attempt anyway.\n")

    require_input("Type 'tool' to prepare the decoding tool: ", "tool")

    # 3. Tool Explanation
    header("🛠️ Step 2: The Tool")
    print("To reverse this, we use the standard Linux command.\n")
    print("The command we are about to run is:\n")
    print(f"   {Colors.GREEN}base64 --decode {INPUT_FILE} > {OUTPUT_FILE}{Colors.END}\n")
    print("🔍 Command breakdown:")
    print(f"   {Colors.BOLD}base64{Colors.END}         → The utility")
    print(f"   {Colors.BOLD}--decode{Colors.END}       → The mode (reverse the encoding)")
    print(f"   {Colors.BOLD}>{Colors.END}              → Redirect output (save to file instead of screen)")
    print(f"   {Colors.BOLD}{OUTPUT_FILE}{Colors.END} → The destination file\n")

    require_input("Type 'run' to execute the command: ", "run")

    # 4. Execution
    print("\n⏳ Decoding transmission...")
    spinner("Processing")

    decoded = decode_base64(input_path, output_path)

    if not decoded:
        print("\n")
        print_error("Decoding failed!")
        print_info(f"The input file may be corrupted or not valid Base64.")
        pause()
        return

    # 5. Success
    print("\n")
    print_success("SUCCESS! Message decoded.")
    print("-" * 50)
    print(f"{Colors.BOLD}{decoded}{Colors.END}")
    print("-" * 50 + "\n")
    print(f"📁 Output saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}")
    print(f"{Colors.CYAN}🔎 Look for the flag format: CCRI-AAAA-1111{Colors.END}")

    pause("Press ENTER to close this terminal...")

# === Entry Point ===
if __name__ == "__main__":
    main()