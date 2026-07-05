#!/usr/bin/env python3

import sys
import subprocess
import shutil
from pathlib import Path
from common import find_project_root, load_unlock_data, get_challenge_file

CHALLENGE_ID = "09_FixScript"

def apply_fix_and_run(script_path: Path, temp_script: Path, operator: str) -> str:
    """Copies the script, patches the math operator, and runs it."""
    try:
        # Copy to temp location for non-destructive validation
        shutil.copy2(script_path, temp_script)
        
        lines = temp_script.read_text(encoding="utf-8").splitlines()
        fixed_lines = [
            f"result = part1 {operator} part2  # <- fixed math" 
            if "result =" in line and any(op in line for op in ["+", "-", "*", "/"])
            else line
            for line in lines
        ]
        temp_script.write_text("\n".join(fixed_lines) + "\n", encoding="utf-8")
        
        # Execute the patched script
        result = subprocess.run(
            [sys.executable, str(temp_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ ERROR during patch/execution: {e}", file=sys.stderr)
        return ""

def validate() -> bool:
    root = find_project_root()
    unlock = load_unlock_data(root, CHALLENGE_ID)
    
    expected_flag = unlock.get("real_flag")
    correct_op = unlock.get("correct_operator", "+")

    if not expected_flag:
        print(f"❌ ERROR: Real flag missing in {CHALLENGE_ID} metadata.", file=sys.stderr)
        return False

    # Get path using our shared helper
    script_path = get_challenge_file(root, CHALLENGE_ID, unlock)
    temp_script = script_path.parent / "temp_validation.py"

    if not script_path.is_file():
        print(f"❌ ERROR: Script not found at {script_path}", file=sys.stderr)
        return False

    try:
        output = apply_fix_and_run(script_path, temp_script, correct_op)
        
        if expected_flag in output:
            print(f"✅ Validation success: found flag {expected_flag}")
            return True
        else:
            print(f"❌ Validation failed: flag {expected_flag} not found in output. Got output: '{output}'", file=sys.stderr)
            return False

    finally:
        # Cleanup temp file
        temp_script.unlink(missing_ok=True)

if __name__ == "__main__":
    success = validate()
    sys.exit(0 if success else 1)