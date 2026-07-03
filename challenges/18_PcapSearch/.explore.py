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
PCAP_FILE = "traffic.pcap"
NOTES_FILENAME = "pcap_notes.txt"

# Matches variants: CCRI-AAAA-1111, AAAA-AAAA-1111, AAAA-1111-AAAA
FLAG_REGEX = re.compile(
    r"(CCRI-[A-Z]{4}-\d{4}|[A-Z]{4}-[A-Z]{4}-\d{4}|[A-Z]{4}-\d{4}-[A-Z]{4})"
)

# === Helpers ===
def check_tshark():
    """Verifies that the tshark packet analysis binary exists within the system execution path."""
    try:
        subprocess.run(
            ["tshark", "-v"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        print_error("tshark is not installed.")
        print_info("On Debian/Parrot: sudo apt install tshark")
        pause()
        sys.exit(1)

# === Flag Extraction Phase ===
def extract_flag_candidates(pcap_path: Path) -> list:
    """Extracts raw packet hex data and passes it through printable character streams to isolate flags."""
    # Using a safely structured system shell pipe to process streaming raw hex output
    cmd = f"tshark -r '{pcap_path.as_posix()}' -Y tcp -T fields -e tcp.payload | xxd -r -p | strings"
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except Exception as e:
        print_error(f"Error running extraction pipeline: {e}")
        return []

    found = set()
    for line in result.stdout.splitlines():
        match = FLAG_REGEX.search(line)
        if match:
            found.add(match.group(0).strip())

    return list(found)

# === Flag-to-Stream Mapping ===
def map_flags_to_streams(pcap_path: Path, flags: list) -> dict:
    """Maps identified flag candidates back to their corresponding TCP conversation stream ID."""
    stream_map = {}
    
    # Extract Stream ID and Payload metrics for every captured packet
    result = subprocess.run(
        ["tshark", "-r", str(pcap_path), "-Y", "tcp", "-T", "fields", "-e", "tcp.stream", "-e", "tcp.payload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )

    stream_data = {}
    for line in result.stdout.strip().splitlines():
        parts = line.split('\t')
        if len(parts) != 2: 
            continue
        stream_id, hex_payload = parts
        try:
            stream_id = int(stream_id)
            stream_data.setdefault(stream_id, []).append(hex_payload)
        except ValueError:
            continue

    # Reassemble payloads to isolate which specific stream owns the targets
    spinner("Mapping streams")
    for stream_id, chunks in stream_data.items():
        full_data = '\n'.join(chunks)
        try:
            # Decode raw hex segments into verifiable text components
            proc = subprocess.Popen(
                ["xxd", "-r", "-p"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )
            stdout, _ = proc.communicate(input=full_data)
            payload = stdout
        except Exception:
            continue

        for flag in flags:
            if flag in payload:
                stream_map.setdefault(stream_id, set()).add(flag)

    return stream_map

# === Display & Interaction ===
def show_stream_summary(pcap_path: Path, sid: int):
    """Reconstructs and displays the complete ASCII output conversation using tshark."""
    header(f"🔗 Stream ID: {sid}")
    print("Using tshark to reconstruct the full TCP conversation:")
    print(f"  {Colors.GREEN}tshark -r traffic.pcap -qz follow,tcp,ascii,{sid}{Colors.END}\n")
    print("-" * 50)
    
    subprocess.run(["tshark", "-r", str(pcap_path), "-qz", f"follow,tcp,ascii,{sid}"])
    print("-" * 50)

def save_summary(pcap_path: Path, sid: int, notes_path: Path):
    """Appends forensic stream transcripts to a localized text archive file on disk."""
    try:
        with notes_path.open("a", encoding="utf-8") as f:
            f.write(f"🔗 Stream ID: {sid}\n")
            subprocess.run(
                ["tshark", "-r", str(pcap_path), "-qz", f"follow,tcp,ascii,{sid}"],
                stdout=f,
                stderr=subprocess.DEVNULL
            )
            f.write("--------------------------------------\n")
        print_success(f"Saved to {notes_path.name}")
    except Exception as e:
        print_error(f"Failed to append conversation stream summary to target note file: {e}")
    time.sleep(1)

# === Main Driver ===
def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    pcap_path = script_dir / PCAP_FILE
    notes_path = script_dir / NOTES_FILENAME
    
    if not pcap_path.is_file():
        print_error(f"Missing file target parameter context: '{pcap_path.name}'")
        sys.exit(1)

    check_tshark()

    # 2. Mission Briefing
    header("📡 PCAP Stream Reconstructor")
    
    print(f"📄 Capture File: {Colors.BOLD}{pcap_path.name}{Colors.END}")
    print(f"🔧 Tool in use: {Colors.BOLD}tshark{Colors.END} (Terminal Wireshark)\n")
    print("🎯 Goal: Identify the TCP Stream containing the hidden flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Concept:** Network traffic consists of thousands of small packets.")
    print("   ➤ **The Strategy:** Stream Reconstruction (reassembling packets into a conversation).")
    print("   ➤ **The Tool:** `tshark` allows us to filter and follow streams.\n")
    
    require_input("Type 'ready' to initialize the analysis: ", "ready")

    # 3. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("We will simulate a forensic workflow:\n")
    
    print("Step 1: Scan for Patterns")
    print("   We search the raw packet payloads for 'CCRI-'.")
    print(f"   {Colors.GREEN}tshark -r traffic.pcap -Y tcp ... | strings | grep CCRI{Colors.END}\n")
    
    print("Step 2: Map to Streams")
    print("   We identify which 'TCP Stream ID' (conversation) contains that pattern.\n")
    
    print("Step 3: Follow Stream")
    print("   We reconstruct the full conversation text.")
    print(f"   {Colors.GREEN}tshark -r traffic.pcap -z follow,tcp,ascii,[ID]{Colors.END}\n")
    
    require_input("Type 'scan' to start Phase 1: ", "scan")

    # 4. Phase 1: Find flag-like values safely using object unlinking
    notes_path.unlink(missing_ok=True)
    
    print(f"\n{Colors.CYAN}🔎 Scanning entire PCAP for flag-like patterns...{Colors.END}")
    spinner("Analyzing packets")

    flags_found = extract_flag_candidates(pcap_path)
    if not flags_found:
        print_error("No flag-like patterns found inside the packet streams.")
        sys.exit(0)

    print(f"\n{Colors.GREEN}✅ Scan complete. Detected {len(flags_found)} potential flag patterns.{Colors.END}")
    print("   (Content hidden to prevent spoilers - map to streams to view)\n")
    
    for f in sorted(flags_found):
        redacted = f[:5] + "****-****"
        print(f"   ➡️  {Colors.YELLOW}{redacted}{Colors.END}")
        
    print()
    require_input("Type 'map' to map these patterns to TCP streams: ", "map")

    # 5. Phase 2: Map flags to streams
    print(f"\n{Colors.CYAN}🔗 Mapping detected flags to their TCP stream IDs...{Colors.END}")
    stream_map = map_flags_to_streams(pcap_path, flags_found)
    
    if not stream_map:
        print_error("No streams matched the candidate flags.")
        sys.exit(0)

    candidates = sorted(stream_map.keys())
    print_success(f"{len(candidates)} TCP stream(s) contain suspect data.\n")
    
    require_input("Type 'investigate' to explore the streams: ", "investigate")

    # 6. Phase 3: Exploration UI
    while True:
        clear_screen()
        print(f"{Colors.CYAN}📜 Candidate Streams:{Colors.END}")
        print("-" * 40)
        for idx, sid in enumerate(candidates, 1):
            count = len(stream_map[sid])
            print(f"{Colors.BOLD}{idx}{Colors.END}. Stream ID: {Colors.YELLOW}{sid}{Colors.END} (Contains {count} hidden candidate(s))")
        print(f"{len(candidates)+1}. Exit\n")

        try:
            choice_str = safe_input(f"{Colors.YELLOW}Choose stream to inspect (1-{len(candidates)+1}): {Colors.END}").strip()
            choice = int(choice_str)
        except ValueError:
            print_error("Invalid input specification parameter context.")
            time.sleep(1)
            continue

        if 1 <= choice <= len(candidates):
            sid = candidates[choice - 1]
            clear_screen()
            
            # The Reveal
            show_stream_summary(pcap_path, sid)

            # Interaction
            while True:
                print("\nOptions:")
                print("1) 🔁 Back to list")
                print(f"2) 💾 Save stream summary (to {NOTES_FILENAME})")
                print("3) 🚪 Exit")
                opt = safe_input(f"{Colors.YELLOW}Choose (1-3): {Colors.END}").strip()
                if opt == "1":
                    break
                elif opt == "2":
                    save_summary(pcap_path, sid, notes_path)
                elif opt == "3":
                    print(f"\n{Colors.CYAN}👋 Done.{Colors.END}")
                    sys.exit(0)
                else:
                    print_error("Invalid choice configuration option selected.")
        elif choice == len(candidates) + 1:
            break
        else:
            print_error("Invalid stream selection index boundary.")
            time.sleep(1)

if __name__ == "__main__":
    main()