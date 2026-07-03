#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

def cleanup():
    """Ensures a clean starting environment by purging any stale flags."""
    Path("flag.txt").unlink(missing_ok=True)

def main():
    bot = Coach("Intercepted Transmission (Base64)")
    
    # Ensure a clean slate
    cleanup()
    
    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction=(
                "We have intercepted a suspicious message.\n"
                "First, move into the challenge directory."
            ),
            command_to_display="cd challenges/02_Base64"
        )

        # === SYNC DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/02_Base64")
        if target_dir.is_dir():
            os.chdir(target_dir)

        # STEP 2: Discovery
        bot.teach_step(
            instruction=(
                "Let's see what files we captured."
            ),
            command_to_display="ls -l"
        )

        # STEP 3: Verification (Using Intel)
        bot.teach_step(
            instruction=(
                "The Mission Brief states that Base64 usually ends with `==`.\n"
                "Let's inspect the file with `cat` to verify it matches this signature."
            ),
            command_to_display="cat encoded.txt"
        )

        # STEP 4: Execution
        bot.teach_step(
            instruction=(
                "It matches the profile (ends in `==`).\n"
                "Decode it using the `base64` tool with the `-d` (decode) flag.\n"
                "Save the output to `flag.txt` so we don't lose it."
            ),
            command_to_display="base64 -d encoded.txt > flag.txt"
        )

        # STEP 5: Verification
        bot.teach_step(
            instruction=(
                "Success! The output was saved to 'flag.txt'.\n"
                "Now, safely read your flag."
            ),
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()

if __name__ == "__main__":
    main()