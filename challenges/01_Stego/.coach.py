#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

def cleanup():
    """Ensures we don't have a stale flag file before starting."""
    Path("flag.txt").unlink(missing_ok=True)

def main():
    bot = Coach("Steganography Decode")
    
    # Ensure clean slate for the existence check later
    cleanup()

    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction=(
                "First, we need to enter the challenge directory.\n"
                "Use the 'cd' (change directory) command."
            ),
            command_to_display="cd challenges/01_Stego"
        )
        
        # === SYNC COACH DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/01_Stego")
        if target_dir.is_dir():
            os.chdir(target_dir)

        # STEP 2: Discovery
        bot.teach_step(
            instruction=(
                "Let's confirm the target file is present."
            ),
            command_to_display="ls -l"
        )

        # STEP 3: The Extraction Loop
        success = False
        flag_file = Path("flag.txt")
        
        while not success:
            bot.teach_loop(
                instruction=(
                    "According to the Mission Brief, this file is locked with a password.\n"
                    "The hint is: 'The password is the most common password in the world.'\n\n"
                    "Use `steghide` to extract the data (`-sf`) and save it to `flag.txt` (`-xf`).\n"
                    "Command format: `steghide extract -sf squirrel.jpg -xf flag.txt -p [PASSWORD]`\n"
                    "Common guesses: `123456`, `password`, `admin`."
                ),
                command_template="steghide extract -sf squirrel.jpg -xf flag.txt -p [PASSWORD]",
                command_prefix="steghide extract",
                command_regex=r"^steghide extract -sf squirrel\.jpg -xf flag\.txt -p .+$"
            )

            # LOGIC CHECK: Verify output file metrics natively via Pathlib
            if flag_file.is_file() and flag_file.stat().st_size > 0:
                success = True
            else:
                print("\n❌ Access Denied. That password did not unlock the file.")
                print("Consult the Mission Brief hint again. What is the literal word for a password?\n")

        # STEP 4: Verification
        bot.teach_step(
            instruction=(
                "🎉 Access Granted! The password was correct.\n"
                "Read the extracted 'flag.txt' file to retrieve the flag."
            ),
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()

if __name__ == "__main__":
    main()