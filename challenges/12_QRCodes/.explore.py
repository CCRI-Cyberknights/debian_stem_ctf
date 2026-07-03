#!/usr/bin/env encoding="utf-8"
import sys
import subprocess
import shutil
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, spinner, print_success, print_error, print_info, resize_terminal, clear_screen

# === Config ===
QR_PATTERN = "qr_*.png"
OUTPUT_FILE = "scan_results.txt"
FLAG_PREFIX = "CCRI-"

def main():
    # 1. Setup
    resize_terminal(35, 90)
    script_dir = Path(__file__).resolve().parent
    output_path = script_dir / OUTPUT_FILE

    # 2. Mission Briefing
    header("📱 Bulk QR Scanner")
    
    print(f"📂 Target Files: {Colors.BOLD}{QR_PATTERN}{Colors.END} (5 images)")
    print(f"🔧 Tool in use: {Colors.BOLD}zbarimg{Colors.END}\n")
    print("🎯 Goal: Scan multiple QR codes instantly to find the one containing the flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Lock:** Data encoded in 2D barcodes.")
    print("   ➤ **The Strategy:** Bulk Scanning (don't check them one by one).")
    print("   ➤ **The Tool:** `zbarimg` decodes images directly in the terminal.\n")
    
    require_input("Type 'ready' to initialize the scanner: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("Scanning these with a phone would take minutes. We can do it in seconds.\n")
    print("We will use the **Wildcard** (`*`) to tell the computer 'all PNG files'.\n")
    
    print("Command to be executed:\n")
    print(f"   {Colors.GREEN}zbarimg {QR_PATTERN} > {OUTPUT_FILE}{Colors.END}\n")
    
    print("🔍 Command breakdown:")
    print(f"   {Colors.BOLD}zbarimg{Colors.END}         → The barcode reader tool")
    print(f"   {Colors.BOLD}{QR_PATTERN:<12}{Colors.END} → The '*' matches 'qr_01.png', 'qr_02.png', etc.")
    print(f"   {Colors.BOLD}> {OUTPUT_FILE}{Colors.END}   → Save all results to a single text file\n")
    
    require_input("Type 'scan' to execute the bulk scan: ", "scan")

    # 4. Execution
    print(f"\n⏳ Scanning all files matching '{QR_PATTERN}'...")
    spinner("Processing images")

    # Check if zbarimg is installed via standard ecosystem paths
    if shutil.which("zbarimg") is None:
        print_error("zbarimg is not installed. Please install 'zbar-tools'.")
        sys.exit(1)

    # Resolve active directory matching images via object-oriented glob sequences
    files_to_scan = sorted(list(script_dir.glob(QR_PATTERN)))
    
    if not files_to_scan:
        print_error("No QR code images found.")
        sys.exit(1)

    try:
        # Stringify resolved path targets before execution pass
        cmd = ["zbarimg"] + [str(f) for f in files_to_scan]
        with output_path.open("w", encoding="utf-8") as out_f:
            subprocess.run(cmd, stdout=out_f, stderr=subprocess.DEVNULL)
            
        print_success("Bulk scan complete.\n")
        
    except Exception as e:
        print_error(f"Scan failed: {e}")
        sys.exit(1)

    # 5. Analysis & Filtering
    print(f"📄 Results saved to: {Colors.BOLD}{OUTPUT_FILE}{Colors.END}")
    print("   Now let's filter the output for the flag.\n")
    
    require_input("Type 'filter' to search for 'CCRI': ", "filter")
    
    print(f"\n🔎 Searching results for flag format...\n")
    
    found_flags = []
    try:
        lines = output_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            if FLAG_PREFIX in line:
                # zbarimg output format is usually "QR-Code:TEXT"
                clean_text = line.split(":", 1)[-1].strip()
                found_flags.append(clean_text)
    except Exception as e:
        print_error(f"Failed to read scan results from disk: {e}")
        sys.exit(1)

    if found_flags:
        print_success(f"Found {len(found_flags)} flag(s)!")
        print("-" * 50)
        for flag in found_flags:
            print(f"   ➡️ {Colors.BOLD}{flag}{Colors.END}")
        print("-" * 50 + "\n")
        
        print(f"{Colors.CYAN}🧠 Success! The wildcard allowed us to check everyone at once.{Colors.END}")
    else:
        print_error("No flags found in the scan results.")
        print_info("Check if the images are valid QR codes.")

    pause("Press ENTER to close this terminal...")

if __name__ == "__main__":
    main()