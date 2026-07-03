#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import pwd
from pathlib import Path

# === Configuration ===
TARGET_USER = "stem_ctf"
TARGET_FOLDER_NAME = "ctf_takehome"

# Items to copy (relative to source_root)
INCLUDE_ITEMS = [
    "challenges", "challenges_solo", "web_version", "ccri_ctf.pyz",
    "start_web_hub.py", "stop_web_hub.py", ".ccri_ctf_root",
    "coach_core.py", "worker_node.py", "exploration_core.py", "reset_environment.py"
]

def apply_permissions(path: Path, uid: int, gid: int):
    """Recursively applies correct ownership and permissions."""
    def is_script(fname): return fname.endswith((".py", ".sh", ".desktop", ".pyz", ".command"))

    # Apply to directory
    os.chown(path, uid, gid)
    os.chmod(path, 0o755)

    # Apply to contents
    for root, dirs, files in os.walk(path):
        for name in dirs + files:
            p = Path(root) / name
            try:
                os.chown(p, uid, gid)
                if p.is_dir():
                    os.chmod(p, 0o755)
                elif is_script(name):
                    os.chmod(p, 0o755)
                else:
                    os.chmod(p, 0o644)
            except OSError as e:
                print(f"⚠️ Could not set perms for {p}: {e}")

def safe_copy(src: Path, dst: Path):
    """Cleans target and performs copy."""
    if dst.exists():
        if dst.is_dir(): shutil.rmtree(dst)
        else: dst.unlink()
    
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

def generate_launcher(launcher_dst: Path):
    """Generates the .desktop file."""
    work_dir = f"$HOME/Desktop/{TARGET_FOLDER_NAME}"
    content = (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=true\n"
        "Name=Launch CCRI CTF Hub (Take-Home)\n"
        f"Exec=bash -c 'cd \"{work_dir}\" && python3 start_web_hub.py'\n"
        f"Icon={work_dir}/icon.png\n"
        "Comment=Start the CyberKnights Challenge Hub\n"
    )
    launcher_dst.write_text(content, encoding="utf-8")

def main():
    # 1. Permission Check
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo) to manage file ownership.")
        sys.exit(1)

    source_root = Path(__file__).resolve().parent
    
    # 2. Identify Target
    try:
        pw_record = pwd.getpwnam(TARGET_USER)
        uid, gid = pw_record.pw_uid, pw_record.pw_gid
    except KeyError:
        print(f"❌ User '{TARGET_USER}' not found.")
        sys.exit(1)

    target_root = Path(f"/home/{TARGET_USER}/Desktop/{TARGET_FOLDER_NAME}")
    print(f"📂 Source: {source_root}\n📥 Target: {target_root}")

    # 3. Create Root & Markers
    target_root.mkdir(parents=True, exist_ok=True)
    if not (source_root / ".ccri_ctf_root").exists():
        (source_root / ".ccri_ctf_root").touch()

    # 4. Copy Files
    for item in INCLUDE_ITEMS:
        src = source_root / item
        if src.exists():
            print(f"➡️ Copying {item}...")
            safe_copy(src, target_root / item)
        else:
            print(f"⚠️ Skipping missing item: {item}")

    # 5. Icon Handling
    icon_src = source_root / "web_version_admin/static/assets/CyberKnights_2.png"
    if icon_src.exists():
        print("🎨 Copying icon...")
        shutil.copy2(icon_src, target_root / "icon.png")

    # 6. Finalize Permissions & Launcher
    print("🔒 Setting permissions and generating launcher...")
    apply_permissions(target_root, uid, gid)
    
    launcher = target_root / "Launch_CCRI_CTF_HUB.desktop"
    generate_launcher(launcher)
    
    # Final chown for the launcher (apply_permissions covers the dir, but just to be safe)
    os.chown(launcher, uid, gid) 
    
    # Trust launcher
    try:
        subprocess.run(["gio", "set", str(launcher), "metadata::trusted", "true"], check=False)
    except Exception:
        pass

    print(f"\n✅ Take-home version deployed to {target_root}")

if __name__ == "__main__":
    main()