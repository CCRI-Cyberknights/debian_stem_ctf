#!/usr/bin/env python3
import sys
import subprocess
import socket
import time
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, print_success, print_error, print_info, resize_terminal, clear_screen, spinner, safe_input

# === Config ===
# No external file dependencies

def check_web_server():
    """Checks if the CTF web server is running on port 5000."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result != 0:
            print_error("The Web Server is not running!")
            print("   This challenge requires the background web services.")
            print(f"   👉 Open a new terminal and run: {Colors.BOLD}python3 start_web_hub.py{Colors.END}\n")
            sys.exit(1)
    except Exception:
        pass

def inspect_portal(portal_name):
    """Runs curl against a specific portal and displays the RAW HTML."""
    url = f"http://localhost:5000/internal/{portal_name}"
    
    print(f"\n🔍 Retrieving Source Code for {Colors.BOLD}{portal_name.upper()}{Colors.END}...")
    print(f"💻 Running: {Colors.CYAN}curl {url}{Colors.END}\n")
    
    spinner("Downloading HTML")
    print("-" * 60)
    
    try:
        # Capture the output so we can analyze it
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True
        )
        
        # Display the Raw HTML
        raw_html = result.stdout
        print(f"{Colors.YELLOW}{raw_html.strip()}{Colors.END}")
        print("-" * 60)
        
        # Check for flag in the raw content
        if "CCRI-" in raw_html:
            print(f"\n{Colors.GREEN}✅ SUSPICIOUS PATTERN DETECTED!{Colors.END}")
            print("   The raw source code contains a flag that was hidden from the rendered view.")
        else:
            print(f"\n{Colors.RED}❌ Clean.{Colors.END} No flags found in this source code.")
            
    except FileNotFoundError:
        print_error("'curl' command not found.")
    
    pause()

def bulk_audit(portals_list):
    """Simulates the Brace Expansion technique."""
    print(f"\n{Colors.CYAN}🚀 Launching Mass Audit (Brace Expansion)...{Colors.END}")
    
    # Construct the brace string: {alpha,beta,gamma...}
    brace_string = ",".join(portals_list)
    url_template = f"http://localhost:5000/internal/{{{brace_string}}}"
    
    print(f"💻 Command: {Colors.BOLD}curl \"{url_template}\"{Colors.END}")
    print("   (This single command will fetch source code for ALL portals at once)\n")
    
    found_any = False
    
    for portal in portals_list:
        url = f"http://localhost:5000/internal/{portal}"
        print(f"   Scanning {portal:<10} ... ", end="", flush=True)
        time.sleep(0.2)
        
        try:
            result = subprocess.run(["curl", "-s", url], capture_output=True, text=True)
            if "CCRI-" in result.stdout:
                print(f"{Colors.GREEN}FOUND!{Colors.END}")
                # Extract flag
                for line in result.stdout.splitlines():
                    if "CCRI-" in line:
                        print(f"      📝 {Colors.BOLD}{line.strip()}{Colors.END}")
                found_any = True
            else:
                print(f"{Colors.RED}Clean{Colors.END}")
                
        except Exception:
            print("Error")

    print("\n")
    if found_any:
        print_success("Audit complete. Target identified.")
    else:
        print_error("Audit complete. No flags found.")
        
    pause()

def main():
    # 1. Setup
    resize_terminal(35, 90)
    check_web_server()

    # 2. Mission Briefing
    header("🌐 Internal Portal Source Audit")
    
    print(f"🔧 Tool in use: {Colors.BOLD}curl{Colors.END}\n")
    print("🎯 Goal: Retrieve the raw HTML source code to find hidden comments or tags.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Concept:** Browsers \"render\" code, hiding comments and scripts.")
    print("   ➤ **The Strategy:** Source Inspection (bypassing the visual layer).")
    print("   ➤ **The Tool:** `curl` prints raw code directly to the terminal.\n")
    
    require_input("Type 'ready' to load the target list: ", "ready")

    # 3. Recon
    header("🔍 Phase 1: Target Identification")
    
    portals = ["alpha", "beta", "gamma", "delta", "omega"]

    print("Scanning local configuration...\n")
    print(f"We have identified {len(portals)} targets:")
    for p in portals:
        print(f" - {p}")
    print("\n")
    
    require_input("Type 'load' to prepare the curl tool: ", "load")

    # 4. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("We have two ways to do this:\n")
    
    print(f"1. {Colors.BOLD}Manual Inspection:{Colors.END}")
    print(f"   {Colors.GREEN}curl http://localhost:5000/internal/alpha{Colors.END}")
    print("   (Repeat 5 times)\n")
    
    print(f"2. {Colors.BOLD}Mass Audit (Brace Expansion):{Colors.END}")
    print(f"   {Colors.GREEN}curl \"http://localhost:5000/internal/{{alpha,beta,gamma...}}\"{Colors.END}")
    print("   (This Linux trick generates all URLs automatically)\n")
    
    require_input("Type 'start' to begin the audit: ", "start")

    # 5. Interactive Loop
    while True:
        clear_screen()
        print(f"{Colors.CYAN}🌐 Portal Audit Console{Colors.END}")
        for i, portal in enumerate(portals, 1):
            print(f"{i}. Inspect {portal.upper()} Source Code")
            
        print(f"\n6. {Colors.BOLD}⚡ Run Mass Audit (Check all){Colors.END}")
        print("7. Exit\n")

        # Wrapped terminal option collection inside safe_input container layer
        choice = safe_input(f"{Colors.YELLOW}Select target (1-7): {Colors.END}").strip()

        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(portals):
                inspect_portal(portals[idx-1])
            elif idx == 6:
                bulk_audit(portals)
            elif idx == 7:
                print(f"\n{Colors.CYAN}👋 Exiting.{Colors.END}")
                break
            else:
                print_error("Invalid option selection.")
                time.sleep(1)
        else:
            print_error("Invalid input matrix parameter.")
            time.sleep(1)

if __name__ == "__main__":
    main()