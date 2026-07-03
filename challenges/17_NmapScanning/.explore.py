#!/usr/bin/env python3
import sys
import subprocess
import time
import socket
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from exploration_core import Colors, header, pause, require_input, print_success, print_error, print_info, resize_terminal, clear_screen, spinner, safe_input

# === Config ===
BINARY_PORT_RANGE = "8000-8100"
BINARY_HOST = "localhost"
BINARY_URL = f"http://{BINARY_HOST}"
SAVE_FILENAME = "nmap_flag_response.txt"

def check_web_server():
    """Checks if the CTF web server is running on port 5000."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        # The web hub runs on 5000, managing the other ports
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result != 0:
            print_error("The Web Server is not running!")
            print("   This challenge requires the background web services.")
            print(f"   👉 Open a new terminal and run: {Colors.BOLD}python3 start_web_hub.py{Colors.END}\n")
            sys.exit(1)
    except Exception:
        pass

# === Nmap Scan ===
def run_nmap_scan() -> str:
    """Executes nmap utility against host ranges."""
    try:
        result = subprocess.run(
            ["nmap", "-sV", "--version-light", f"-p{BINARY_PORT_RANGE}", BINARY_HOST],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return result.stdout
    except FileNotFoundError:
        print_error("`nmap` is not installed.")
        sys.exit(1)

def extract_open_ports(scan_output: str) -> list:
    """Parses open tcp listener ports from scan output streams."""
    ports = []
    for line in scan_output.splitlines():
        if "open" in line and "tcp" in line:
            try:
                # nmap format: 8000/tcp open  http
                port = line.split("/")[0].strip()
                ports.append(port)
            except Exception:
                continue
    return ports

# === Curl Requests ===
def fetch_port_response(port: str) -> str:
    """Interrogates identified network interfaces via curl."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "2", f"{BINARY_URL}:{port}"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            return f"[Connection Error] {result.stderr.strip()}"
        return result.stdout.strip()
    except FileNotFoundError:
        print_error("`curl` is not installed.")
        sys.exit(1)

# === Main Program ===
def main():
    # 1. Setup
    resize_terminal(35, 90)
    check_web_server()
    
    script_dir = Path(__file__).resolve().parent
    save_file_path = script_dir / SAVE_FILENAME
    
    # 2. Mission Briefing
    header("🛰️  Nmap Port Scanner")
    
    print(f"🎯 Target Range: {Colors.BOLD}{BINARY_PORT_RANGE}{Colors.END}")
    print(f"🔧 Tool in use: {Colors.BOLD}nmap{Colors.END} (Network Mapper)\n")
    print("🎯 Goal: Scan the network range, enumerate services, and find the flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Concept:** Hackers use Port Scanners to knock on every \"door\". ")
    print("   ➤ **The Tool:** `nmap` is the industry standard for network discovery. ")
    print("   ➤ **The Warning:** Most ports are decoys. Only one has the real flag.\n")
    
    require_input("Type 'ready' to initialize the scanner: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("We are about to run a real port scan against your local simulation.")
    print("Command to be executed:\n")
    print(f"   {Colors.GREEN}nmap -sV -p {BINARY_PORT_RANGE} {BINARY_HOST}{Colors.END}\n")
    
    print("🔍 Command breakdown:")
    print("   {Colors.BOLD}-sV{Colors.END}                  → Service Version detection (try to identify the software)")
    print(f"   {Colors.BOLD}-p {BINARY_PORT_RANGE}{Colors.END}    → Only scan this specific range (saves time)")
    print(f"   {Colors.BOLD}{BINARY_HOST}{Colors.END}           → The target IP/Hostname\n")
    
    require_input("Type 'scan' to execute the nmap command: ", "scan")

    # 4. Scanning Phase
    print(f"\n📡 Scanning ports {BINARY_PORT_RANGE}...")
    spinner("Knocking on ports")

    scan_output = run_nmap_scan()
    open_ports = extract_open_ports(scan_output)
    
    print_success("Scan complete.\n")
    print(f"{Colors.CYAN}📝 Raw Nmap Output:{Colors.END}")
    print("--------------------------------------")
    # Show only the interesting lines to keep it clean
    for line in scan_output.splitlines():
        if "PORT" in line or "open" in line:
            print(f"   {line}")
    print("--------------------------------------\n")

    if not open_ports:
        print_error("No open ports found. Is the web server running?")
        sys.exit(1)

    print(f"Found {len(open_ports)} open ports: {Colors.BOLD}{', '.join(open_ports)}{Colors.END}\n")
    require_input("Type 'enumerate' to inspect each service: ", "enumerate")

    # 5. Enumeration Phase (Interactive Loop)
    while True:
        clear_screen()
        print(f"{Colors.CYAN}🌐 Service Enumeration:{Colors.END}")
        print("======================================")
        for idx, port in enumerate(open_ports, 1):
            print(f"{Colors.BOLD}{idx:2d}. Port {port}{Colors.END}")
        print(f"\n{len(open_ports)+1:2d}. 🚪 Exit Scanner")

        try:
            choice_str = safe_input(f"\n{Colors.YELLOW}🔍 Select a port to investigate (1-{len(open_ports)+1}): {Colors.END}").strip()
            choice = int(choice_str)
        except ValueError:
            print_error("Invalid input specification entry.")
            time.sleep(1)
            continue

        if 1 <= choice <= len(open_ports):
            port = open_ports[choice - 1]
            
            clear_screen()
            print(f"🔎 Interrogating Service on Port {Colors.BOLD}{port}{Colors.END}...")
            print(f"💻 Running: {Colors.GREEN}curl -s {BINARY_URL}:{port}{Colors.END}\n")
            
            response = fetch_port_response(port)
            
            print("👇 Service Response:")
            print("======================================")
            if "CCRI-" in response:
                print(f"{Colors.GREEN}{response}{Colors.END}")
            else:
                print(f"{Colors.YELLOW}{response}{Colors.END}")
            print("======================================\n")
            
            if "CCRI-" in response:
                print(f"{Colors.GREEN}✅ FLAG DETECTED!{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Decoy/Junk Data.{Colors.END} Keep looking.")

            # Save option
            while True:
                save_opt = safe_input(f"\n💾 Save this evidence? (y/n): ").strip().lower()
                if save_opt == 'y':
                    try:
                        with save_file_path.open("a", encoding="utf-8") as f:
                            f.write(f"--- Port {port} ---\n{response}\n\n")
                        print_success(f"Saved to {SAVE_FILENAME}")
                    except Exception as e:
                        print_error(f"Save failed: {e}")
                    time.sleep(1)
                    break
                elif save_opt == 'n':
                    break

        elif choice == len(open_ports) + 1:
            print(f"\n{Colors.CYAN}👋 Exiting scanner.{Colors.END}")
            break
        else:
            print_error("Invalid option choice range value.")
            time.sleep(1)

if __name__ == "__main__":
    main()