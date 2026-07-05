#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import pwd
from pathlib import Path

# === Configuration ===
TARGET_FOLDER_NAME = "ccri_ctf_solo"

INCLUDE_ITEMS = [
    "challenges_solo", "web_version", "ccri_ctf.pyz",
    "start_web_hub.py", "stop_web_hub.py", ".ccri_ctf_root",
    "coach_core.py", "worker_node.py", "LICENSE", "reset_environment.py"
]

def apply_permissions(path: Path, uid: int, gid: int):
    """Recursively set ownership and setgid permissions."""
    def is_script(fname): return fname.endswith((".py", ".sh", ".desktop", ".pyz", ".command"))

    for root, dirs, files in os.walk(path):
        current = Path(root)
        os.chown(current, uid, gid)
        os.chmod(current, 0o2775)  # SetGID bit for shared group access
        
        for name in files:
            p = current / name
            os.chown(p, uid, gid)
            os.chmod(p, 0o775 if is_script(name) else 0o664)

def prune_guided_content(target_root: Path):
    """Removes Guided/Exploration Mode content to keep the Solo environment clean."""
    print("🧹 Pruning guided-mode content...")
    
    # 1. Remove Guided challenges folder
    if (target_root / "challenges").exists():
        shutil.rmtree(target_root / "challenges")

    # 2. Clean up specific web_version artifacts
    web_dir = target_root / "web_version"
    if web_dir.exists():
        (web_dir / "challenges.json").unlink(missing_ok=True)
        (web_dir / "templates/challenge.html").unlink(missing_ok=True)

def setup_launcher(target_desktop: Path, uid: int, gid: int):
    """Generates the Solo .desktop launcher."""
    launcher = target_desktop / "Launch_CCRI_CTF_Solo.desktop"
    
    content = (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=true\n"
        "Name=Launch CCRI CTF (Solo)\n"
        f"Exec=bash -c 'cd $HOME/Desktop/{TARGET_FOLDER_NAME} && python3 start_web_hub.py'\n"
        f"Icon={target_desktop}/{TARGET_FOLDER_NAME}/icon.png\n"
        "Comment=Start the Solo Capture-The-Flag Hub\n"
    )
    
    launcher.write_text(content, encoding="utf-8")
    os.chown(launcher, uid, gid)
    os.chmod(launcher, 0o775)
    
    # Trust launcher
    subprocess.run(["gio", "set", str(launcher), "metadata::trusted", "true"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def main():
    # 1. Elevation Pass
    if os.geteuid() != 0:
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)

    # 2. Identify Target User Dynamically
    # Capture the non-root calling context via SUDO_USER environment checks
    target_user = os.environ.get("SUDO_USER")
    if not target_user:
        file_uid = Path(__file__).resolve().stat().st_uid
        if file_uid != 0:
            target_user = pwd.getpwuid(file_uid).pw_name
        else:
            print("❌ Could not automatically determine the target user. Please run via 'sudo user script.py'.")
            sys.exit(1)

    try:
        pw = pwd.getpwnam(target_user)
        uid, gid = pw.pw_uid, pw.pw_gid
    except KeyError:
        print(f"❌ Target user '{target_user}' lookup failed system registration checks.")
        sys.exit(1)

    source_root = Path(__file__).resolve().parent
    target_root = Path(f"/home/{target_user}/Desktop/{TARGET_FOLDER_NAME}")

    print(f"📂 Source: {source_root}\n📥 Target: {target_root} (User: {target_user})")

    # 3. Clean and Copy
    if target_root.exists():
        shutil.rmtree(target_root)
    target_root.mkdir(parents=True, exist_ok=True)
    
    for item in INCLUDE_ITEMS:
        src = source_root / item
        if src.exists():
            print(f"➡️ Copying {item}...")
            if src.is_dir(): shutil.copytree(src, target_root / item)
            else: shutil.copy2(src, target_root / item)

    # 4. Prune Guided Content
    prune_guided_content(target_root)

    # 5. Icon/Permissions/Launcher
    icon_src = source_root / "web_version_admin/static/assets/CyberKnights_2.png"
    if icon_src.exists():
        shutil.copy2(icon_src, target_root / "icon.png")

    apply_permissions(target_root, uid, gid)
    setup_launcher(target_root.parent, uid, gid)

    print(f"\n✅ Solo-Only Version Deployed Smoothly to {target_root}")

if __name__ == "__main__":
    main()