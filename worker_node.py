#!/usr/bin/env python3
import socket
import subprocess
import os
import sys
import time
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        return 

    host = '127.0.0.1'
    port = int(sys.argv[1])

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        time.sleep(1) 
        s.connect((host, port))
    except (ConnectionRefusedError, TimeoutError):
        # Gracefully drop out if connection fails to bind
        return

    # Info for the custom prompt
    user = os.getenv('USER', 'student')
    
    print("🔗 Connected to Coach.")
    print("💻 Commands entered in the Coach window will execute here.\n")

    while True:
        # Dynamic CWD lookup using Pathlib object trees
        current_path = Path.cwd()
        home_path    = Path.home()
        
        if current_path == home_path:
            display_cwd = "~"
        elif home_path in current_path.parents:
            display_cwd = f"~/{current_path.relative_to(home_path).as_posix()}"
        else:
            display_cwd = current_path.as_posix()

        # Receive Command
        try:
            data = s.recv(4096).decode('utf-8')
        except Exception:
            break
            
        if not data or data == "EXIT":
            print("\n👋 Session ended.")
            break

        # === SILENT COMMAND HANDLER ===
        # If the command starts with SILENT:, run it inside background filters
        if data.startswith("SILENT:"):
            silent_cmd = data[7:]
            try:
                subprocess.run(
                    silent_cmd, 
                    shell=True, 
                    executable="/bin/bash",
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
            s.sendall(b"DONE")
            continue
        # ==============================

        # Normal Prompt Display
        prompt = f"\033[1;32m{user}@term\033[0m:\033[1;34m{display_cwd}\033[0m$ "
        print(prompt, end="", flush=True)

        # Automated typing simulation engine
        for char in data:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.01) 
        print() 

        # State Persistent 'cd' Handler
        if data.strip().startswith("cd "):
            path_target = data.strip()[3:].strip()
            try:
                os.chdir(Path(path_target).expanduser())
            except FileNotFoundError:
                print(f"❌ bash: cd: {path_target}: No such file or directory")
            except Exception as e:
                print(f"❌ cd error: {e}")
            s.sendall(b"DONE")
            continue

        # Execute target commands inside native bash execution layers
        try:
            subprocess.run(data, shell=True, executable="/bin/bash")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        s.sendall(b"DONE")

    s.close()

if __name__ == "__main__":
    main()