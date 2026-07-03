#!/usr/bin/env python3
import sys
import subprocess
import time
import shlex
import os  # Maintained strictly for environmental controls and process teardown
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
import exploration_core 
from exploration_core import Colors, header, pause, require_input, print_success, print_error, print_info, clear_screen, safe_input

# === THE FIX: Patch the module itself ===
# This ensures that even if 'header()' calls resize_terminal internally,
# it uses THIS version (allowing for the bigger window logic).
original_resize = exploration_core.resize_terminal

def safe_resize(rows=35, cols=90):
    # If in Big Mode, IGNORE small resize requests
    if os.environ.get("BIGGER_TERMINAL") == "1":
        # Force the big size (48x140)
        sys.stdout.write(f"\x1b[8;48;140t")
        sys.stdout.flush()
    else:
        # Standard behavior
        original_resize(rows, cols)

# Overwrite the function in the library
exploration_core.resize_terminal = safe_resize

# === Config ===
DUMP_FILE = "ps_dump.txt"
OUTPUT_FILE = "process_output.txt"

def relaunch_in_bigger_terminal(script_path: Path):
    """Re-executes the script in a larger terminal window for visibility."""
    if os.environ.get("BIGGER_TERMINAL") == "1":
        return

    os.environ["BIGGER_TERMINAL"] = "1"
    abs_script = script_path.resolve()
    print_info("Launching in a larger terminal window for better visibility...")
    time.sleep(1)

    try:
        # Try MATE Terminal first (common in Kali/Parrot)
        subprocess.Popen([
            "mate-terminal",
            "--geometry=140x48", 
            "--", "bash", "-c",
            f"printf '\\033[8;48;140t'; python3 '{abs_script.as_posix()}'; exec bash"
        ])
        time.sleep(1)
        os._exit(0)
    except FileNotFoundError:
        # Fallback: Just try to resize the current window and proceed
        safe_resize(48, 140)

def load_process_map(ps_dump_path: Path) -> dict:
    """Parses ps_dump.txt and returns a {binary: full_command} mapping."""
    proc_map = {}
    if not ps_dump_path.is_file():
        return {}
    try:
        with ps_dump_path.open("r", encoding="utf-8", errors="ignore") as f:
            next(f)  # Skip header row
            for line in f:
                # ps aux columns: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
                parts = line.strip().split(maxsplit=10)
                if len(parts) == 11:
                    full_cmd = parts[10]
                    try:
                        args = shlex.split(full_cmd)
                        binary = args[0] if args else full_cmd
                    except Exception:
                        binary = full_cmd

                    if binary not in proc_map:
                        proc_map[binary] = full_cmd
    except Exception:
        return {}
    return proc_map

def inspect_process(binary: str, ps_dump_path: Path) -> str:
    clear_screen()
    print(f"\n🔍 Inspecting process: {Colors.BOLD}{binary}{Colors.END}")
    print("-" * 50)
    time.sleep(0.5)

    try:
        # Use grep to find the specific tracking lines
        result = subprocess.run(
            ["grep", binary, str(ps_dump_path)],
            stdout=subprocess.PIPE,
            text=True
        )
        if not result.stdout.strip():
            print_error("No matching process found.")
        else:
            # Format output for readability (wrap long lines)
            formatted = result.stdout.replace("--", "\n    --")
            print(f"{Colors.YELLOW}{formatted}{Colors.END}")
            print("-" * 50)
            return formatted
    except Exception as e:
        print_error(f"Error inspecting process: {e}")
    return ""

def save_output(text: str, path: Path):
    try:
        path.write_text(text, encoding="utf-8")
        print_success(f"Output saved to {path.name}")
    except Exception as e:
        print_error(f"Failed to save output target stream: {e}")

def main():
    # 1. Setup paths via Object Model
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent
    ps_dump_path = script_dir / DUMP_FILE
    output_path = script_dir / OUTPUT_FILE

    # 2. Relaunch Check
    relaunch_in_bigger_terminal(script_path)

    # 3. Resize window environment context
    time.sleep(0.2)
    safe_resize() 
    
    # 4. Mission Briefing
    header("🖥️  Process Inspection")
    
    print(f"📄 Snapshot File: {Colors.BOLD}{DUMP_FILE}{Colors.END}")
    print(f"🔧 Strategy: {Colors.BOLD}Process Auditing{Colors.END}\n")
    print("🎯 Goal: Identify the rogue process carrying the flag in its options.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Concept:** Every program is a process.")
    print("   ➤ **The Clue:** Malware often hides secrets in **Command Line Options**.")
    print("   ➤ **The Task:** Filter the snapshot to find the option `--flag=...`\n")
    
    require_input("Type 'ready' to learn how to audit processes: ", "ready")

    if not ps_dump_path.is_file():
        print_error(f"{DUMP_FILE} not found inside environment path context.")
        sys.exit(1)

    # 5. Tool Explanation
    header("🛠️ Behind the Scenes")
    print("This challenge is based on the output of the Linux command:\n")
    print(f"   {Colors.GREEN}ps aux{Colors.END}")
    print("\nThat output was saved into ps_dump.txt. Each line contains:")
    print(f"   {Colors.BOLD}USER  PID  CPU% ... COMMAND{Colors.END}")
    print("   (The COMMAND column shows exactly how the program was started)\n")
    
    print("In a real terminal, you would search it like this:\n")
    print(f"   {Colors.GREEN}grep '--flag=' ps_dump.txt{Colors.END}\n")
    print("This helper script will list the binaries for you to inspect manually.\n")
    
    require_input("Type 'start' to view the process list: ", "start")

    proc_map = load_process_map(ps_dump_path)
    display_names = sorted(proc_map.keys())

    # 6. Interactive Loop
    while True:
        clear_screen()
        print(f"{Colors.CYAN}📂 Process List (Unique Binaries):{Colors.END}")
        print("-" * 40)
        for idx, name in enumerate(display_names, 1):
            # Truncate long names for menu layout rendering
            display_name = (name[:50] + '..') if len(name) > 50 else name
            print(f"{Colors.BOLD}{idx}{Colors.END}. {display_name}")
        print(f"{len(display_names) + 1}. Exit")
        print("-" * 40)

        try:
            choice_str = safe_input(f"\n{Colors.YELLOW}Select a process to inspect (1-{len(display_names)+1}): {Colors.END}").strip()
            if not choice_str.isdigit():
                raise ValueError
            choice = int(choice_str)
        except ValueError:
            print_error("Invalid input. Please enter a valid menu list item number.")
            pause()
            continue

        if 1 <= choice <= len(display_names):
            binary = display_names[choice - 1]
            result_text = inspect_process(binary, ps_dump_path)

            if result_text:
                if "CCRI-" in result_text:
                    print(f"\n{Colors.GREEN}✅ SUSPICIOUS OPTION FOUND!{Colors.END}")
                    print(f"   The flag is hidden in the options of {Colors.BOLD}{Path(binary).name}{Colors.END}.")

                while True:
                    print("\nOptions:")
                    print("1. Return to process list")
                    print(f"2. Save this output to a file ({OUTPUT_FILE})\n")
                    option = safe_input(f"{Colors.YELLOW}Choose an option (1-2): {Colors.END}").strip()

                    if option == "1":
                        break
                    elif option == "2":
                        save_output(result_text, output_path)
                        pause()
                        break
                    else:
                        print_error("Invalid choice specification context entry.")
        elif choice == len(display_names) + 1:
            print(f"\n{Colors.CYAN}👋 Exiting.{Colors.END}")
            break
        else:
            print_error("Invalid selection index constraint.")
            pause()

if __name__ == "__main__":
    main()