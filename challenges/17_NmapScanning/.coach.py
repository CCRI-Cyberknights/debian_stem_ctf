#!/usr/bin/env python3
import sys
import os
import socket
from pathlib import Path

# === Import Core via Pathlib ===
sys.path.append(str(Path(__file__).resolve().parents[2]))
from coach_core import Coach

def check_web_server():
    """Checks if the CTF web server is running on port 5000 (which manages the other ports)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5000))
        sock.close()
        
        if result != 0:
            print("\n❌ ERROR: The Web Server is not running!")
            print("This challenge requires the background web services.")
            print("👉 Please open a new terminal tab and run: python3 start_web_hub.py\n")
            sys.exit(1)
    except Exception:
        pass

def cleanup_artifacts():
    """Removes lingering workspace tracking artifacts safely."""
    Path("flag.txt").unlink(missing_ok=True)

def main():
    check_web_server()
    
    bot = Coach("Network Mapper (nmap)")
    
    # Ensure a fresh execution canvas
    cleanup_artifacts()
    
    bot.start()

    try:
        # STEP 1: Navigation
        bot.teach_step(
            instruction="First, enter the challenge directory.",
            command_to_display="cd challenges/17_NmapScanning"
        )
        
        # === SYNC DIRECTORY VIA PATHLIB ===
        target_dir = Path("challenges/17_NmapScanning")
        if target_dir.is_dir():
            os.chdir(target_dir)
        # ==================================

        # STEP 2: The Intel
        bot.teach_step(
            instruction=(
                "Good hackers read documentation before attacking.\n"
                "The `README.md` file contains the intelligence for this mission.\n\n"
                "Read it to find out which ports we need to scan."
            ),
            command_to_display="cat README.md"
        )

        # STEP 3: The Scan
        bot.teach_step(
            instruction=(
                "The README states services are listening between ports **8000 and 8100**.\n"
                "Run `nmap` focused on just that specific range to save time."
            ),
            command_to_display="nmap -p 8000-8100 localhost"
        )

        # STEP 4: Enumeration Loop (Trial & Error)
        found_it = False
        
        while not found_it:
            # 4a. Ask them to check a port
            bot.teach_loop(
                instruction=(
                    "You found multiple open ports! Most are decoys.\n"
                    "We need to check them one by one.\n\n"
                    "Pick an open port from the list above and `curl` it.\n"
                    "**Look for 'CCRI-...' in the output.**"
                ),
                command_template="curl localhost:[PORT]",
                command_prefix="curl localhost:",
                command_regex=r"^curl localhost:\d+$"
            )

            # 4b. Interactive Confirmation
            print("\n" + "="*60)
            user_response = input("❓ Did you see the flag 'CCRI-...' in that output? (yes/no): ").strip().lower()
            print("="*60 + "\n")

            if user_response in ['yes', 'y']:
                found_it = True
            else:
                print("❌ Okay, that was a decoy. Pick a different port from your nmap list.\n")

        # STEP 5: The Capture
        bot.teach_loop(
            instruction=(
                "Great work finding the needle in the haystack!\n"
                "Now, run that **exact command** again, but add `> flag.txt` to save the evidence."
            ),
            command_template="curl localhost:[PORT] > flag.txt",
            command_prefix="curl localhost:",
            command_regex=r"^curl localhost:\d+ > flag\.txt$",
            clean_files=["flag.txt"]
        )

        # STEP 6: Verify
        bot.teach_step(
            instruction=(
                "Success! You filtered out the decoys and captured the real target.\n"
                "Read 'flag.txt' to finish."
            ),
            command_to_display="cat flag.txt"
        )

        bot.finish()

    except KeyboardInterrupt:
        bot.finish()
    finally:
        cleanup_artifacts()

if __name__ == "__main__":
    main()