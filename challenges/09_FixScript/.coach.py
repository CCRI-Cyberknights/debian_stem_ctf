#!/usr/bin/env python3
import sys
import os
import re
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

def get_script_data(filepath: Path):
    """
    Reads the file target to extract part1, part2, and the active bug operator.
    Returns: (part1, part2, bug_symbol) or (None, None, None) on failure.
    """
    if not filepath.is_file():
        return None, None, "?"
        
    try:
        content = filepath.read_text(encoding="utf-8")
        
        # Isolate script parameter states using explicit token mapping groups
        p1 = re.search(r"part1\s*=\s*(\d+)", content)
        p2 = re.search(r"part2\s*=\s*(\d+)", content)
        bug = re.search(r"code\s*=\s*part1\s*([\+\-\*\/])\s*part2", content)
        
        if p1 and p2 and bug:
            return int(p1.group(1)), int(p2.group(1)), bug.group(1)
            
    except Exception:
        pass
    return None, None, "?"

def generate_math_table(p1, p2):
    """
    Generates an alignment grid evaluating all 4 mathematical operators.
    Returns the formatted text table string along with the valid target symbol.
    """
    if p1 is None or p2 is None:
        return "Could not parse workspace data variables.", "+"

    correct_symbol = "+"
    
    # Render table schema headers
    table =  "\n   Operator | Calculation       | Result      | Status\n"
    table += "   ---------|-------------------|-------------|-----------\n"
    
    for symbol, name in [("+", "Add"), ("-", "Sub"), ("*", "Mult"), ("/", "Div")]:
        try:
            # Safely evaluate primitive operator metrics
            val = eval(f"{p1} {symbol} {p2}")
            
            if isinstance(val, int):
                val_str = f"{val}"
            elif val.is_integer():
                val = int(val)
                val_str = f"{val}"
            else:
                val_str = f"{val:.2f}"
            
            # Logic constraint check: Valid target codes fit between 1000 and 9999
            if 1000 <= val <= 9999 and val == int(val):
                status = "✅ VALID (Target)"
                correct_symbol = symbol
            else:
                status = "❌ Invalid"
                
            table += f"      {symbol}     | {p1} {symbol} {p2:<6} | {val_str:<11} | {status}\n"
            
        except ZeroDivisionError:
             table += f"      {symbol}     | {p1} {symbol} {p2:<6} | ERROR       | ❌ Invalid\n"

    return table, correct_symbol

def cleanup():
    """Purges any lingering flag extractions from previous lab evaluations."""
    Path("flag.txt").unlink(missing_ok=True)

def main():
    bot = Coach("Python Debugging")
    
    # Ensure environment surface starts completely clean
    cleanup()

    # Just-In-Time evaluation lookups matching core execution environment shapes
    try:
        path_options = [
            Path("challenges/09_FixScript/broken_flag.py"),
            Path("broken_flag.py")
        ]
        target_path = None
        for path_opt in path_options:
            if path_opt.is_file():
                target_path = path_opt
                break

        if target_path:
            p1, p2, bug_symbol = get_script_data(target_path)
            math_table, correct_symbol = generate_math_table(p1, p2)
            
            symbol_map = {"+": "Plus (+)", "-": "Minus (-)", "*": "Multiply (*)", "/": "Divide (/)"}
            correct_name = symbol_map.get(correct_symbol, "Operator")
        else:
            p1, p2, bug_symbol = 0, 0, "?"
            math_table = "Target logic file was not discovered."
            correct_symbol = "+"
            correct_name = "Plus"

    except Exception:
        p1, p2, bug_symbol = 0, 0, "?"
        math_table = "Internal runtime parsing error analyzing target file."
        correct_symbol = "+"
        correct_name = "Plus"

    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction="First, enter the challenge directory.",
            command_to_display="cd challenges/09_FixScript"
        )
        
        # === SYNC DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/09_FixScript")
        if target_dir.is_dir():
            os.chdir(target_dir)

        # STEP 2: Discovery
        bot.teach_step(
            instruction="List the files. You will see 'broken_flag.py'.",
            command_to_display="ls -l"
        )

        # STEP 3: Read Source Code
        bot.teach_step(
            instruction=(
                "**Before we run it, we must read it.**\n"
                "Use `cat` to see the code.\n"
                "Look for the variables `part1`, `part2`, and the math equation."
            ),
            command_to_display="cat broken_flag.py"
        )

        # STEP 4: Run the broken code
        bot.teach_step(
            instruction=(
                "Now run the script to see the bug in action.\n"
                "The output is likely scrambled or wrong because the operator is incorrect."
            ),
            command_to_display="python3 broken_flag.py"
        )

        # STEP 5: Debug Analysis & Editing
        bot.teach_step(
            instruction=(
                f"**Analysis:**\n"
                f"The code uses the operator `{bug_symbol}`.\n"
                f"The variables are: `part1={p1}`, `part2={p2}`.\n\n"
                "**Let's calculate all possibilities to find the 4-digit code:**\n"
                f"{math_table}\n"
                f"The table proves the correct operator is **{correct_name}**.\n\n"
                "👉 **Task:**\n"
                "   1. Run `nano broken_flag.py`.\n"
                "   2. **Click the terminal** to focus.\n"
                f"   3. Use **Arrow Keys** to find `{bug_symbol}`.\n"
                f"   4. Delete it and type `{correct_symbol}`.\n"
                "   5. **Save & Exit:** `Ctrl+X`, then `Y`, then `Enter`."
            ),
            command_to_display="nano broken_flag.py"
        )

        # STEP 6: Verify and Save
        bot.teach_loop(
            instruction=(
                "Now that the logic is fixed, run the script and **save the output** to 'flag.txt'."
            ),
            command_template="python3 broken_flag.py > flag.txt",
            command_prefix="python3 broken_flag.py",
            command_regex=r"^python3 broken_flag\.py > flag\.txt$",
            clean_files=["flag.txt"]
        )

        # STEP 7: Final Confirm
        bot.teach_step(
            instruction="Success! Read 'flag.txt' to see the corrected flag.",
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()

if __name__ == "__main__":
    main()