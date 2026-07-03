#!/usr/bin/env python3
import sys
import os
import time
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

# === CONFIGURATION & TOOL DATA ===
TOOL_PATH = Path("decoder.py")
FLAG_PATH = Path("flag.txt")

SOLVER_SCRIPT_CONTENT = r"""#!/usr/bin/env python3
import sys

def decrypt(text, key):
    res = []
    key_idx = 0
    key = key.lower()
    for c in text:
        if c.isalpha():
            base = 65 if c.isupper() else 97
            k = ord(key[key_idx % len(key)]) - 97
            res.append(chr((ord(c) - base - k) % 26 + base))
            key_idx += 1
        else:
            res.append(c)
    return "".join(res)

if len(sys.argv) < 3:
    print("Usage: python3 decoder.py <file> <key>")
    sys.exit(1)

try:
    with open(sys.argv[1], 'r') as f:
        data = f.read().strip()
    
    key = sys.argv[2]
    print(decrypt(data, key))
except Exception as e:
    print(f"Error: {e}")
"""

def create_tool():
    """Writes the ephemeral decoding tool to the current working directory."""
    TOOL_PATH.write_text(SOLVER_SCRIPT_CONTENT, encoding="utf-8")
    TOOL_PATH.chmod(0o755)

def cleanup_tool():
    """Removes the ephemeral solver script and flag tracking targets safely."""
    TOOL_PATH.unlink(missing_ok=True)
    FLAG_PATH.unlink(missing_ok=True)

def main():
    # Ensure clean state before launching context
    cleanup_tool()
    
    bot = Coach("Vigenère Cipher Breaker")
    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction=(
                "First, move into the challenge directory."
            ),
            command_to_display="cd challenges/04_Vigenere"
        )
        
        # === SYNC DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/04_Vigenere")
        if target_dir.is_dir():
            os.chdir(target_dir)

        # STEP 2: Discovery
        bot.teach_step(
            instruction="Check the directory contents.",
            command_to_display="ls -l"
        )

        # STEP 3: Inspection
        bot.teach_step(
            instruction=(
                "Read the encrypted file.\n"
                "It looks like random letters. The README says this is Vigenère."
            ),
            command_to_display="cat cipher.txt"
        )

        # STEP 4: Tool Provisioning
        print("\n[Coach] 🛠️  The README notes that you need a tool for this.")
        print("[Coach] 📡  I am generating a Python script named 'decoder.py' for you now...")
        create_tool()
        time.sleep(1)
        
        bot.teach_step(
            instruction=(
                "I have created `decoder.py`.\n"
                "Verify it is now in your directory."
            ),
            command_to_display="ls -l"
        )

        # STEP 5: Code Inspection
        bot.teach_step(
            instruction=(
                "Always inspect unknown scripts before running them.\n"
                "Read the script to see how it shifts the letters back based on the key."
            ),
            command_to_display="cat decoder.py"
        )

        # STEP 6: Execution
        bot.teach_loop(
            instruction=(
                "Vigenère requires a Key.\n"
                "The Mission Brief asks: 'What is the opposite of logout?' -> login.\n\n"
                "Run the decoder using that key and redirect `>` the output to `flag.txt`.\n"
                "Syntax: `python3 decoder.py cipher.txt [KEY] > flag.txt`"
            ),
            command_template="python3 decoder.py cipher.txt login > flag.txt",
            command_prefix="python3 decoder.py",
            command_regex=r"^python3 decoder\.py cipher\.txt login > flag\.txt$",
            clean_files=["flag.txt"]
        )

        # STEP 7: Verification
        bot.teach_step(
            instruction=(
                "Success! The tool decrypted the data.\n"
                "Read 'flag.txt' to finish."
            ),
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()
    finally:
        # Final runtime cleanup cycle
        cleanup_tool()

if __name__ == "__main__":
    main()