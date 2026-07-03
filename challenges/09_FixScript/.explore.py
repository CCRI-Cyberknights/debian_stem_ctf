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
SCRIPT_NAME = "broken_flag.py"
OUTPUT_FLAG_FILE = "flag.txt"

def run_python_script(script_path: Path) -> str:
    """Executes the target python script using the synchronized virtual environment interpreter."""
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except FileNotFoundError:
        print_error("Python interpreter context was not found.")
        sys.exit(1)

def patch_operator_in_script(script_path: Path, new_operator: str):
    """Parses and updates the math operator inside the target script natively via Pathlib."""
    try:
        lines = script_path.read_text(encoding="utf-8").splitlines()
        new_lines = []
        
        for line in lines:
            if "code = part1" in line:
                # Replace the current mathematical operator structure cleanly using regex arrays
                new_line = re.sub(r"part1\s*[\+\-\*\/]\s*part2", f"part1 {new_operator} part2", line)
                new_lines.append(new_line)
            else:
                new_lines.append(line)
                
        script_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    except Exception as e:
        print_error(f"Error patching target code workspace: {e}")
        sys.exit(1)

def main():
    # 1. Setup
    resize_terminal(35, 90)
    
    script_dir = Path(__file__).resolve().parent
    broken_script = script_dir / SCRIPT_NAME
    flag_output_file = script_dir / OUTPUT_FLAG_FILE

    if not broken_script.is_file():
        print_error(f"{SCRIPT_NAME} not found inside scope: {script_dir.as_posix()}.")
        sys.exit(1)

    # 2. Mission Briefing
    header("🐛 Python Debugging Challenge")
    
    print(f"📄 Broken script: {Colors.BOLD}{SCRIPT_NAME}{Colors.END}")
    print(f"🔧 Strategy: {Colors.BOLD}Debugging{Colors.END}\n")
    print("🎯 Goal: Fix the logic error in the script to reveal the flag.\n")
    
    print(f"{Colors.CYAN}🧠 Intelligence Report (from README):{Colors.END}")
    print("   ➤ **The Problem:** The script executes, but the math logic is flawed.")
    print("   ➤ **The Clue:** It calculates a 4-digit code using `part1` and `part2`.")
    print("   ➤ **The Strategy:** Read -> Analyze -> Edit.")
    print("   ➤ **The Task:** Find the correct operator (+, -, *, /).\n")
    
    require_input("Type 'ready' to inspect the source code: ", "ready")

    # 3. File Inspection
    header("🔍 Step 1: Read Source Code")
    print(f"Opening {Colors.BOLD}{SCRIPT_NAME}{Colors.END}...\n")
    
    print("-" * 50)
    try:
        lines = broken_script.read_text(encoding="utf-8").splitlines()
        for line in lines:
            # Highlight the broken logic target line
            if "code = part1" in line:
                print(f"{Colors.YELLOW}{Colors.BOLD}>> {line.strip()} <<  (THIS IS THE BUG){Colors.END}")
            else:
                print(line)
    except Exception as e:
        print_error(f"Could not read script payload structure: {e}")
        
    print("-" * 50 + "\n")
    
    print("👀 Notice the line highlighted above? That determines the security code.")
    print("   We need to change that operator to make the math work out.\n")

    require_input("Type 'run' to test the current broken script: ", "run")

    # 4. Interactive Debug Loop
    while True:
        clear_screen()
        header("💻 Debug Console")
        print(f"Running: {Colors.BOLD}python {SCRIPT_NAME}{Colors.END}")
        print("-" * 50)
        output = run_python_script(broken_script)
        print(output)
        print("-" * 50 + "\n")

        # Verify operational execution state outcomes
        if "CCRI-" in output and "INVALID" not in output and "Error" not in output:
            match = re.search(r"CCRI-[A-Z0-9]{4}-\d{4}", output)
            if match:
                flag = match.group(0)
                print_success(f"SUCCESS! Logic Fixed. Flag: {Colors.BOLD}{flag}{Colors.END}")
                try:
                    flag_output_file.write_text(flag + "\n", encoding="utf-8")
                    print(f"📁 Saved to: {Colors.BOLD}{OUTPUT_FLAG_FILE}{Colors.END}")
                except Exception as e:
                    print_error(f"Failed to record resolved cleartext flag data to disk: {e}")
                pause("Press ENTER to finish...")
                break

        print(f"{Colors.RED}⚠️ The output looks wrong. The math operator is incorrect.{Colors.END}\n")
        
        print(f"{Colors.CYAN}🛠️ Select a patch to apply:{Colors.END}")
        print("   [+] Addition       (part1 + part2)")
        print("   [-] Subtraction    (part1 - part2)")
        print("   [*] Multiplication (part1 * part2)")
        print("   [/] Division       (part1 / part2)")
        print("   [q] Quit")
        
        # Wrapped input collection using safe_input wrapper mechanics
        op = safe_input(f"\n{Colors.YELLOW}Enter operator (+, -, *, /): {Colors.END}").strip()
        
        if op == 'q':
            break
            
        if op in ["+", "-", "*", "/"]:
            print(f"\n✏️ Patching {SCRIPT_NAME} with operator '{op}'...")
            patch_operator_in_script(broken_script, op)
            spinner("Updating code")
        else:
            print(f"{Colors.RED}❌ Invalid operator definition context selected.{Colors.END}")
            time.sleep(1)

if __name__ == "__main__":
    main()