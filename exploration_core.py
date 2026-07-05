#!/usr/bin/env python3
import sys
import os
import time
import signal  # 🔌 Added to handle instant terminal process closure

# === 🎨 STANDARD COLORS (Matches Coach Mode) ===
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

# === 🛡️ SAFE INTERRUPT INPUT WRAPPER ===
def safe_input(prompt_text: str) -> str:
    """
    Wraps the standard input collection layer to securely absorb Ctrl+C and Ctrl+D.
    Prevents ugly Python tracebacks from spilling into the student's terminal space.
    """
    try:
        return input(prompt_text)
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write(f"\n\n{Colors.RED}👋 Exploration session canceled. Closing window...{Colors.END}\n")
        sys.stdout.flush()
        # Cleanly close the window immediately if they cancel mid-challenge
        try:
            os.kill(os.getppid(), signal.SIGTERM)
        except Exception:
            pass
        sys.exit(0)

# === 🛠️ TERMINAL UTILITIES ===
def resize_terminal(rows=35, cols=90):
    """
    Neutralized to allow the Window Manager and --maximize flag 
    to handle responsive scaling across different monitor resolutions.
    """
    pass  # Keeps the terminal beautifully full-screen instead of forcing small pixel boundaries

def clear_screen():
    """Wipes the active terminal screen space clean."""
    os.system('clear' if os.name == 'posix' else 'cls')

def header(title_text):
    """Standardized header format for all automated exploration challenges."""
    resize_terminal()
    clear_screen()
    print(f"{Colors.CYAN}{Colors.BOLD}{title_text}{Colors.END}")
    print("=" * 50 + "\n")

def pause(prompt=None):
    """Pauses step-by-step execution until the student presses Enter."""
    if prompt is None:
        prompt = f"{Colors.YELLOW}🔸 Press ENTER to continue...{Colors.END}"
    
    safe_input(prompt)
    
    # 🌟 THE ZOMBIE TERMINAL KILL SWITCH:
    # If the pause message specifically asks to close the terminal, 
    # signal the parent terminal wrapper to shut down immediately.
    if prompt and "close this terminal" in prompt.lower():
        try:
            os.kill(os.getppid(), signal.SIGTERM)
        except Exception:
            pass

def require_input(prompt, expected):
    """Forces the user to type a specific validation phrase to proceed forward."""
    while True:
        answer = safe_input(f"{Colors.YELLOW}{prompt}{Colors.END}").strip().lower()
        if answer == expected.lower():
            return
        print(f"{Colors.RED}↪  Please type '{expected}' to continue!{Colors.END}\n")

def spinner(message="Working", duration=2.0, interval=0.15):
    """Displays a clean, animated terminal frame spinner to mimic background processing state."""
    frames = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{Colors.CYAN}{message}... {frame}{Colors.END}")
        sys.stdout.flush()
        time.sleep(interval)
        i += 1
    sys.stdout.write("\r" + " " * (len(message) + 10) + "\r")
    sys.stdout.flush()

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")
