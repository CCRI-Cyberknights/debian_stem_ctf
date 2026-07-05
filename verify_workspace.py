#!/usr/bin/env python3

import os
import sys
import time
import json
import subprocess
import urllib.request
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ ERROR: 'requests' module missing. Install it via 'pip3 install requests'.", file=sys.stderr)
    sys.exit(1)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

BASE_URL = "http://127.0.0.1:5000"

def print_banner(text: str, color: str = BLUE):
    print("\n" + color + BOLD + "=" * 60)
    print(f" 🚀 {text}")
    print("=" * 60 + RESET)

def wait_for_server(url: str, timeout: int = 5) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def run_subprocess_stage(step_num: int, name: str, script_name: str, root_dir: Path, args: list = None) -> bool:
    script_path = root_dir / script_name
    print_banner(f"STAGE {step_num}: {name} ({script_name})")
    
    if not script_path.is_file():
        print(f"{RED}❌ CONFIGURATION FAILURE: Script file missing: {script_path}{RESET}", file=sys.stderr)
        return False

    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, cwd=root_dir, stdout=sys.stdout, stderr=sys.stderr, check=False
        )
        elapsed = time.time() - start_time
        if result.returncode == 0:
            print(f"\n{GREEN}✅ {name} Phase Finished Successfully! ({elapsed:.1f}s){RESET}")
            return True
        print(f"\n{RED}❌ {name} Phase Failed with exit code: {result.returncode} ({elapsed:.1f}s){RESET}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"\n{RED}❌ Exception occurred during stage execution: {e}{RESET}", file=sys.stderr)
        return False

def run_web_matrix_stage(step_num: int, root_dir: Path) -> bool:
    print_banner(f"STAGE {step_num}: Web Matrix Routing & API Probe")
    
    modes = {
        "guided": {
            "cfg": root_dir / "web_version_admin" / "challenges.json",
            "unl": root_dir / "web_version_admin" / "validation_unlocks.json"
        },
        "solo": {
            "cfg": root_dir / "web_version_admin" / "challenges_solo.json",
            "unl": root_dir / "web_version_admin" / "validation_unlocks_solo.json"
        }
    }

    failures = 0
    start_time = time.time()

    for mode, paths in modes.items():
        if not paths["cfg"].is_file() or not paths["unl"].is_file():
            print(f"{YELLOW}⚠️  Skipping web check: Configuration missing for {mode} mode.{RESET}")
            continue

        with paths["cfg"].open("r", encoding="utf-8") as f:
            challenges = json.load(f)
        with paths["unl"].open("r", encoding="utf-8") as f:
            unlocks = json.load(f)

        print(f"\n🌐 Probing Web Matrix: [{mode.upper()}]")
        print("-" * 50)

        # 🔄 Establish a persistent state session context for this mode block
        session = requests.Session()
        web_mode = "regular" if mode == "guided" else "solo"
        
        # Initialize the server-side session cookie state
        try:
            session.get(f"{BASE_URL}/set_mode/{web_mode}", timeout=2)
        except requests.RequestException as e:
            print(f"❌ Failed to initialize session mode context for {web_mode}: {e}")
            failures += 1
            continue

        for challenge_id in challenges:
            challenge_url = f"{BASE_URL}/challenge/{challenge_id}"
            try:
                res = session.get(challenge_url, timeout=2)
                if res.status_code != 200:
                    print(f"❌ Route Failure: {challenge_id} [{mode}] returned status {res.status_code}")
                    failures += 1
                    continue
            except requests.RequestException as e:
                print(f"❌ Connection error on {challenge_id} [{mode}]: {e}")
                failures += 1
                continue

            challenge_unlock = unlocks.get(challenge_id, {})
            real_flag = challenge_unlock.get("real_flag")
            if not real_flag:
                continue

            try:
                submit_url = f"{BASE_URL}/submit_flag/{challenge_id}"
                payload = {"flag": real_flag}
                
                res = session.post(submit_url, json=payload, timeout=2)
                
                # Fixed the string check to look for "correct" to match the server's response
                if res.status_code != 200 or "correct" not in res.text.lower():
                    print(f"❌ Flag Validation Rejected: {challenge_id} ({mode})")
                    print(f"   -> HTTP Status: {res.status_code}")
                    print(f"   -> Server Response: {res.text[:150].strip()}")
                    failures += 1
                else:
                    print(f"✅ Web Routing + Flag Submission Success: {challenge_id} ({mode})")
            except requests.RequestException as e:
                print(f"❌ Network transmission error for {challenge_id}: {e}")
                failures += 1

    elapsed = time.time() - start_time
    if failures == 0:
        print(f"\n{GREEN}✅ Web Matrix Phase Finished Successfully! ({elapsed:.1f}s){RESET}")
        return True
    print(f"\n{RED}❌ Web Matrix Phase Failed with {failures} routing anomalies. ({elapsed:.1f}s){RESET}", file=sys.stderr)
    return False

def main():
    root_dir = Path(__file__).resolve().parent
    master_start = time.time()

    print(f"{BLUE}{BOLD}🚦 CCRI STEMDay Full Stack Infrastructure Verification Pipeline{RESET}")
    print(f"Working Directory Context: {root_dir}\n")

    # --- STAGE 1: Cold Asset Generation ---
    gen_success = run_subprocess_stage(1, "Asset & Flag Random Generation", "generate_all_flags.py", root_dir)
    if not gen_success:
        print(f"\n{RED}{BOLD}🚨 PIPELINE BREAK: Generation failed. Aborting infrastructure verification.{RESET}", file=sys.stderr)
        sys.exit(1)

    # --- SERVER LIFECYCLE START ---
    print(f"\n{BLUE}{BOLD}🌐 Initializing Background Web Hub for Live Challenge Validation...{RESET}")
    
    # Open a file descriptor to catch startup errors
    boot_log_path = root_dir / ".server_boot.log"
    boot_log = boot_log_path.open("w", encoding="utf-8")

    # Pass --testing directly as a command line argument
    web_process = subprocess.Popen(
        [sys.executable, str(root_dir / "start_web_hub.py"), "--testing"],
        stdout=boot_log,
        stderr=boot_log,
        cwd=root_dir
    )

    stage_results = [("Asset & Flag Random Generation", True)]
    web_server_live = False

    try:
        if wait_for_server(BASE_URL, timeout=6):
            print(f"{GREEN}✅ Environment services successfully verified as active and listening.{RESET}")
            web_server_live = True
        else:
            boot_log.close() # Close it so we can read it
            print(f"{RED}❌ CRITICAL: Web Hub failed to bind within the window limit.{RESET}", file=sys.stderr)
            print(f"{YELLOW}📄 Reading Web Hub boot stderr output logs below:{RESET}\n" + "-"*60, file=sys.stderr)
            print(boot_log_path.read_text(encoding="utf-8", errors="ignore"), file=sys.stderr)
            print("-"*60, file=sys.stderr)
            
            stage_results.extend([
                ("Guided Forensic Key Extraction", False),
                ("Solo Verification Simulation", False),
                ("Web Matrix Routing & API Probe", False)
            ])

        if web_server_live:
            # --- STAGE 2: Guided Forensic Validation ---
            guided_success = run_subprocess_stage(2, "Guided Forensic Key Extraction", "validate_all_flags.py", root_dir, ["guided"])
            stage_results.append(("Guided Forensic Key Extraction", guided_success))
            
            # --- STAGE 3: Solo Forensic Validation ---
            if guided_success:
                solo_success = run_subprocess_stage(3, "Solo Verification Simulation", "validate_all_flags.py", root_dir, ["solo"])
                stage_results.append(("Solo Verification Simulation", solo_success))
            else:
                solo_success = False
                stage_results.append(("Solo Verification Simulation", False))

            # --- STAGE 4: Inline Web Matrix & Endpoint Probe ---
            if solo_success:
                matrix_success = run_web_matrix_stage(4, root_dir)
                stage_results.append(("Web Matrix Routing & API Probe", matrix_success))
            else:
                stage_results.append(("Web Matrix Routing & API Probe", False))

    finally:
        # --- SERVER LIFECYCLE TEARDOWN ---
        print(f"\n{BLUE}🛑 Terminating background test environment context...{RESET}")
        web_process.terminate()
        web_process.wait()
        
        if not boot_log.closed:
            boot_log.close()
            
        subprocess.run([sys.executable, str(root_dir / "stop_web_hub.py")], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Clean up temporary boot log file
        if boot_log_path.exists():
            boot_log_path.unlink()
        print("🔒 Network sockets closed and workspace cleaned.")

    # --- Final Dashboard Report ---
    total_elapsed = time.time() - master_start
    print("\n" + "=" * 60)
    print(f"{BOLD}📊 Final Workspace Diagnostics Report Summary{RESET}")
    print("=" * 60)
    
    all_passed = True
    for name, status in stage_results:
        status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"
        if not status:
            all_passed = False
        print(f" * {name:<40} -> [{status_text}]")

    print("-" * 60)
    if all_passed:
        print(f"{GREEN}{BOLD}🎉 WORKSPACE IS COMPLETELY GREEN! Deployment is ready.{RESET} (Total: {total_elapsed:.1f}s)\n")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}🚨 PIPELINE FAILURE DETECTED: Review the validation logs above.{RESET} (Total: {total_elapsed:.1f}s)\n")
        sys.exit(1)

if __name__ == "__main__":
    main()