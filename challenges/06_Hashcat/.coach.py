#!/usr/bin/env python3
import sys
import os
import subprocess
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

# === CONFIGURATION & TARGET PATHS ===
TOOL_PATH = Path(".assembler.py")
POTFILE_PATH = Path("hashcat.potfile")
HASHES_PATH = Path("hashes.txt")
FLAG_PATH = Path("flag.txt")

ASSEMBLER_SCRIPT_CONTENT = r"""#!/usr/bin/env python3
import sys
import subprocess
from pathlib import Path

def main():
    parts = ["encoded_segments1.txt", "encoded_segments2.txt", "encoded_segments3.txt"]
    decoded_lines = []

    # 1. Decode each file using modern Pathlib validation checks
    for p in parts:
        part_path = Path(p)
        if not part_path.is_file():
            print(f"ERROR: Could not find '{p}'. Did you unzip the segments?", file=sys.stderr)
            sys.exit(1)
        
        # Decode using system base64 processing pipeline
        res = subprocess.run(["base64", "-d", str(part_path)], capture_output=True, text=True)
        decoded_lines.append(res.stdout.splitlines())

    # 2. Merge (Zip) segment lines together systematically
    print("--- REASSEMBLED FLAGS ---")
    
    if decoded_lines:
        num_candidates = len(decoded_lines[0])
        for i in range(num_candidates):
            segment_pieces = []
            for d in decoded_lines:
                if i < len(d):
                    segment_pieces.append(d[i].strip())
                else:
                    segment_pieces.append("MISSING")
            print("-".join(segment_pieces))

if __name__ == "__main__":
    main()
"""

def create_tool():
    """Writes the data fragment assembler tool to the current working directory."""
    TOOL_PATH.write_text(ASSEMBLER_SCRIPT_CONTENT, encoding="utf-8")
    TOOL_PATH.chmod(0o755)

def cleanup_tool():
    """Removes ephemeral processing scripts, hashes databases, and segment extractions."""
    TOOL_PATH.unlink(missing_ok=True)
    POTFILE_PATH.unlink(missing_ok=True)
    FLAG_PATH.unlink(missing_ok=True)
    
    # Safely clear out any residual segment text file extractions
    for i in range(1, 4):
        Path(f"encoded_segments{i}.txt").unlink(missing_ok=True)

def get_ordered_passwords():
    """
    Reads hashcat.potfile to map hashes to passwords, ensuring we return them
    in the precise order matching the hashes.txt input manifest sequence.
    """
    passwords = []
    cracked = {}
    
    # Map Hash String -> Plaintext Password
    if POTFILE_PATH.is_file():
        with POTFILE_PATH.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" in line:
                    h, p = line.strip().split(":", 1)
                    cracked[h] = p
    
    # Retrieve plaintext keys matching active execution sequencing
    if HASHES_PATH.is_file():
        with HASHES_PATH.open("r", encoding="utf-8") as f:
            for line in f:
                h = line.strip()
                if h:
                    passwords.append(cracked.get(h, "unknown"))
    
    # Structural padding array loop guard
    while len(passwords) < 3:
        passwords.append("unknown")
        
    return passwords

def main():
    bot = Coach("Hashcat ChainCrack")
    
    # Ensure clean slate before initialization
    cleanup_tool()
    
    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction=(
                "First, enter the challenge directory."
            ),
            command_to_display="cd challenges/06_Hashcat"
        )
        
        # === SYNC DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/06_Hashcat")
        if target_dir.is_dir():
            os.chdir(target_dir)

        # STEP 2: Discovery
        bot.teach_step(
            instruction=(
                "Let's survey the battlefield.\n"
                "Use 'ls -R' (recursive list) to see the segments inside the folder."
            ),
            command_to_display="ls -R"
        )

        # STEP 3: Cracking
        bot.teach_step(
            instruction=(
                "We need to crack the hashes to get the passwords.\n"
                "   `-m 0`           → MD5 Mode\n"
                "   `-a 0`           → Dictionary Attack\n"
                "   `--potfile-path` → Saves cracked passwords locally\n\n"
                "Run the attack:"
            ),
            command_to_display="hashcat -m 0 -a 0 hashes.txt wordlist.txt --potfile-path hashcat.potfile"
        )

        # STEP 4: Reveal
        bot.teach_step(
            instruction=(
                "The passwords are saved in the potfile. Now we reveal them using `--show`.\n"
                "💡 Tip: Press **Up Arrow** to recall the command, then add ` --show`."
            ),
            command_to_display="hashcat -m 0 -a 0 hashes.txt wordlist.txt --potfile-path hashcat.potfile --show"
        )

        # === READ LOCAL RESULTS ===
        p1, p2, p3 = get_ordered_passwords()[:3]

        # STEP 5: Unlock Part 1
        bot.teach_loop(
            instruction=(
                "Hashcat's `--show` output matches the input order.\n"
                "1. The **first line** matches the **first zip** (part1).\n"
                f"2. That password is **{p1}**.\n\n"
                "Use it to unzip Part 1:"
            ),
            command_template=f"unzip -o -P {p1} segments/part1.zip",
            command_prefix="unzip -o -P ",
            command_regex=fr"^unzip -o -P {p1} segments/part1\.zip$",
            clean_files=["encoded_segments1.txt"]
        )

        # STEP 6: Unlock Part 2
        bot.teach_loop(
            instruction=(
                "The **second line** matches **part2.zip**.\n"
                f"The password is **{p2}**.\n\n"
                "Unlock Part 2:"
            ),
            command_template=f"unzip -o -P {p2} segments/part2.zip",
            command_prefix="unzip -o -P ",
            command_regex=fr"^unzip -o -P {p2} segments/part2\.zip$",
            clean_files=["encoded_segments2.txt"]
        )

        # STEP 7: Unlock Part 3
        bot.teach_loop(
            instruction=(
                "And the **third line** matches **part3.zip**.\n"
                f"The password is **{p3}**.\n\n"
                "Unlock Part 3:"
            ),
            command_template=f"unzip -o -P {p3} segments/part3.zip",
            command_prefix="unzip -o -P ",
            command_regex=fr"^unzip -o -P {p3} segments/part3\.zip$",
            clean_files=["encoded_segments3.txt"]
        )

        # STEP 8: Tool Provisioning
        print("\n[Coach] 🧠  The Mission Brief says we need to 'Assemble' the data.")
        print("[Coach] ⚠️  We have three separate files. Combining them by hand is slow.")
        print("[Coach] 📡  I am generating a helper script `.assembler.py` for you now...")
        create_tool()

        bot.teach_step(
            instruction=(
                "I have created `.assembler.py`.\n"
                "Always inspect code before running it. Read the script now."
            ),
            command_to_display="cat .assembler.py"
        )

        # STEP 9: Assembly
        bot.teach_loop(
            instruction=(
                "The code looks safe (it decodes Base64 and merges the lines).\n"
                "Run it and save the result to 'flag.txt'."
            ),
            command_template="python3 .assembler.py > flag.txt",
            command_prefix="python3 .assembler.py",
            command_regex=r"^python3 \.assembler\.py > flag\.txt$",
            clean_files=["flag.txt"]
        )

        # STEP 10: Finish
        bot.teach_step(
            instruction=(
                "Success! Read 'flag.txt' to see the reassembled flag."
            ),
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()
    finally:
        cleanup_tool()

if __name__ == "__main__":
    main()