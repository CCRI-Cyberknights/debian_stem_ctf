#!/usr/bin/env python3
import os
import sys
import subprocess
import signal
import shutil
import time
from pathlib import Path

# === CCRI CTF Hub Stopper (Venv-Safe & Batch-Optimized) ===

# Simplified patterns: pgrep -f matches the whole command line string.
# By matching just the target files, we seamlessly catch whatever interpreter runs them (.venv, system, etc.)
PATTERNS = [
    r"ccri_ctf\.pyz",              # Student zipapp
    r"web_version_admin/server\.py" # Admin server
]

GUIDED_PORT_RANGE = (8000, 8100)
SOLO_PORT_RANGE   = (9000, 9100)
WEB_PORT          = 5000

def find_project_root():
    """Walk upwards to find the .ccri_ctf_root marker."""
    dir_path = os.path.abspath(os.getcwd())
    while dir_path != "/":
        if os.path.exists(os.path.join(dir_path, ".ccri_ctf_root")):
            return dir_path
        dir_path = os.path.dirname(dir_path)
    print("❌ ERROR: Could not find .ccri_ctf_root marker. Are you inside the CTF folder?")
    sys.exit(1)

def pids_from_pattern(pattern: str):
    """Return a list of PIDs matching a pgrep -f pattern."""
    try:
        res = subprocess.run(
            ["pgrep", "-f", pattern],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        if res.returncode != 0 or not res.stdout.strip():
            return []
        return [int(x) for x in res.stdout.strip().splitlines() if x.strip().isdigit()]
    except FileNotFoundError:
        print("❌ ERROR: 'pgrep' not found.")
        return []
    except Exception as e:
        print(f"❌ pgrep failed for pattern {pattern}: {e}")
        return []

def term_then_kill(pids, grace=2.0):
    """SIGTERM then SIGKILL after a grace period if still alive."""
    dead = set()
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            dead.add(pid)
    if pids:
        time.sleep(grace)

    # Check who’s still alive
    still = []
    for pid in pids:
        if pid in dead:
            continue
        try:
            os.kill(pid, 0)
            still.append(pid)
        except ProcessLookupError:
            pass

    # SIGKILL stragglers
    for pid in still:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

    if pids:
        killed = [str(p) for p in pids]
        print(f"🛑 Terminated PIDs: {' '.join(killed)} (SIGTERM→SIGKILL as needed)")
    return len(pids)

def clear_port_range(start: int, end: int):
    """Kill any process listening on a range of TCP ports simultaneously (Batch Optimized)."""
    if shutil.which("lsof"):
        # Native lsof supports dash notation for batch port ranges (e.g., :8000-8100)
        res = subprocess.run(
            ["lsof", "-ti", f":{start}-{end}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        pids = [int(x) for x in res.stdout.strip().splitlines() if x.strip().isdigit()]
    elif shutil.which("fuser"):
        # Fallback to fuser batch syntax
        res = subprocess.run(
            ["fuser", "-n", "tcp", f"{start}-{end}"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )
        pids = [int(x) for x in res.stdout.strip().split()] if res.stdout else []
    else:
        print(f"⚠️ Neither 'lsof' nor 'fuser' present; skipping cleanup for range {start}-{end}.")
        return 0

    if not pids:
        return 0
    return term_then_kill(pids)

def main():
    project_root = find_project_root()

    # 🛡️ SELF-CORRECTING VIRTUAL ENVIRONMENT GUARD
    venv_python = os.path.join(project_root, ".venv", "bin", "python3")
    if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        os.execv(venv_python, [venv_python] + sys.argv)

    print("🛑 Stopping CCRI CTF Hub...\n")

    # 1) Kill by process patterns (student/admin) using flexible regex strings
    total_matched = 0
    for pat in PATTERNS:
        pids = pids_from_pattern(pat)
        if pids:
            print(f"🔍 Pattern match `{pat}` → PIDs: {' '.join(map(str, pids))}")
            total_matched += term_then_kill(pids)
        else:
            print(f"ℹ️ No active processes matched `{pat}`")

    # 2) Ensure web port 5000 is free
    print("\n🔧 Ensuring core web port 5000 is clear...")
    cleared = clear_port_range(WEB_PORT, WEB_PORT)
    if cleared:
        print(f"✅ Cleared {cleared} process(es) on port {WEB_PORT}")
    else:
        print("ℹ️ Port 5000 already clear.")

    # 3) Optimized batch sweeps for mock challenges and ranges
    print(f"\n🔧 Sweeping guided ports {GUIDED_PORT_RANGE[0]}–{GUIDED_PORT_RANGE[1]} in batch...")
    g = clear_port_range(*GUIDED_PORT_RANGE)
    print("✅ Cleared guided range processes." if g else "ℹ️ Guided range already clear.")

    print(f"\n🔧 Sweeping solo ports {SOLO_PORT_RANGE[0]}–{SOLO_PORT_RANGE[1]} in batch...")
    s = clear_port_range(*SOLO_PORT_RANGE)
    print("✅ Cleared solo range processes." if s else "ℹ️ Solo range already clear.")

    print("\n🎯 Cleanup complete.")

if __name__ == "__main__":
    main()