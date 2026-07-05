#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import shutil

def find_project_root():
    dir_path = os.path.abspath(os.getcwd())
    while dir_path != "/":
        if os.path.exists(os.path.join(dir_path, ".ccri_ctf_root")):
            return dir_path
        dir_path = os.path.dirname(dir_path)
    print("❌ ERROR: Could not find .ccri_ctf_root marker. Are you inside the CTF folder?")
    sys.exit(1)

def launch_process(cmd, log_file):
    print(f"🟢 Launching: {' '.join(cmd)}")
    with open(log_file, "w") as log:
        subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, preexec_fn=os.setpgrp)
    time.sleep(2)
    try:
        subprocess.check_call(
            ["curl", "-s", "http://127.0.0.1:5000/healthz"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print("✅ Web server responded on /healthz.")
    except subprocess.CalledProcessError:
        # Try root path as fallback probe
        try:
            subprocess.check_call(["curl", "-s", "http://127.0.0.1:5000"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ Web server started successfully.")
        except subprocess.CalledProcessError:
            print(f"❌ ERROR: Web server failed to start. Check logs at: {log_file}")
            sys.exit(1)

def open_browser():
    # 🛡️ PIPELINE SAFEGUARD LAYER
    if "--testing" in sys.argv:
        print("🌐 Testing environment detected. Skipping browser auto-launch.")
        return

    print("🌐 Opening http://127.0.0.1:5000 ...")
    
    # 🛡️ PROCESS DETACHMENT LAYER
    # We must enforce preexec_fn=os.setpgrp across ALL pathways so the 
    # child launcher survives when the parent deployment script exits.
    if shutil.which("xdg-open"):
        subprocess.Popen(["xdg-open", "http://127.0.0.1:5000"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                         preexec_fn=os.setpgrp)
        return
        
    for binary in ("firefox-esr", "firefox"):
        browser_path = shutil.which(binary)
        if browser_path:
            subprocess.Popen([browser_path, "--new-window", "http://127.0.0.1:5000"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                             preexec_fn=os.setpgrp)
            return
            
    print("❌ No browser launcher found. Open manually: http://127.0.0.1:5000")

def main():
    project_root = find_project_root()

    # 🛡️ SELF-CORRECTING VIRTUAL ENVIRONMENT GUARD
    # Dynamically find the local sandbox interpreter relative to project folder
    venv_python = os.path.join(project_root, ".venv", "bin", "python3")
    if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        # Hot-swap the running process seamlessly to execute inside the sandbox
        os.execv(venv_python, [venv_python] + sys.argv)

    print("🚀 Starting the CCRI CTF Hub...\n")

    pyz_path      = os.path.join(project_root, "ccri_ctf.pyz")
    admin_server  = os.path.join(project_root, "web_version_admin", "server.py")
    has_pyz       = os.path.isfile(pyz_path)
    has_admin     = os.path.isfile(admin_server)

    if not has_pyz and not has_admin:
        print("❌ ERROR: Neither ccri_ctf.pyz (student) nor web_version_admin/server.py (admin) found.")
        sys.exit(1)

    # Decide mode: prompt only if both exist
    if has_admin and has_pyz:
        print("🧭 Both Admin and Student builds detected.")
        choice = input("🔄 Launch which mode? [1] Admin  [2] Student (default): ").strip()
        base_mode = "admin" if choice == "1" else "student"
    elif has_admin:
        print("🛠️ Only Admin build detected.")
        base_mode = "admin"
    else:
        print("🎓 Only Student build detected.")
        base_mode = "student"

    os.environ["CCRI_CTF_MODE"] = base_mode

    # If already running on 5000, don't launch another
    try:
        subprocess.check_call(["lsof", "-i:5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("🌐 Web server already running (port 5000). Skipping launch.")
    except subprocess.CalledProcessError:
        log_file = os.path.join(project_root, "web_server.log")
        if base_mode == "admin":
            cmd = [sys.executable, admin_server]
        else:
            # Student ALWAYS runs the .pyz; no fallbacks.
            cmd = [sys.executable, pyz_path]
        launch_process(cmd, log_file)

    open_browser()
    print("✅ CCRI CTF Hub is ready!")

if __name__ == "__main__":
    main()
