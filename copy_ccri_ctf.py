#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import pwd
import grp
from pathlib import Path

# === Configuration ===
TARGET_GROUP = "ccri_ctf"
TARGET_FOLDER_NAME = "ccri_ctf"

INCLUDE_ITEMS = [
    "challenges", "challenges_solo", "web_version", "ccri_ctf.pyz",
    "start_web_hub.py", "stop_web_hub.py", ".ccri_ctf_root",
    "coach_core.py", "worker_node.py", "exploration_core.py", "reset_environment.py"
]

def ensure_group_membership(group_name: str, usernames: list):
    """Create group if needed and add users."""
    try:
        grp.getgrnam(group_name)
    except KeyError:
        print(f"➕ Creating group '{group_name}'...")
        subprocess.run(["groupadd", group_name], check=True)

    for user in usernames:
        try:
            subprocess.run(["usermod", "-aG", group_name, user], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Could not add user {user} to group {group_name}: {e}")
    
    return grp.getgrnam(group_name).gr_gid

def apply_permissions(path: Path, uid: int, gid: int):
    """Recursively set ownership and setgid permissions."""
    def is_script(fname): return fname.endswith((".py", ".sh", ".desktop", ".pyz", ".command"))

    # Walk and apply
    for root, dirs, files in os.walk(path):
        current = Path(root)
        os.chown(current, uid, gid)
        os.chmod(current, 0o2775)  # SetGID bit for shared group access
        
        for name in files:
            p = current / name
            try:
                os.chown(p, uid, gid)
                os.chmod(p, 0o775 if is_script(name) else 0o664)
            except OSError as e:
                print(f"⚠️ Could not set perms for {p}: {e}")

def setup_launcher(target_desktop: Path, uid: int, gid: int):
    """Generates the .desktop launcher."""
    launcher = target_desktop / "Launch_CCRI_CTF_Hub.desktop"
    icon = target_desktop / TARGET_FOLDER_NAME / "icon.png"
    
    content = (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=true\n"
        "Name=Launch CCRI CTF Hub\n"
        f"Exec=bash -c 'cd $HOME/Desktop/{TARGET_FOLDER_NAME} && python3 start_web_hub.py'\n"
        f"Icon={icon if icon.exists() else 'utilities-terminal'}\n"
        "Comment=Start the CyberKnights Challenge Hub\n"
    )
    
    launcher.write_text(content, encoding="utf-8")
    os.chown(launcher, uid, gid)
    os.chmod(launcher, 0o775)
    
    # Mark as trusted
    subprocess.run(["gio", "set", str(launcher), "metadata::trusted", "true"], 
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def main():
    # 1. Elevation Pass
    if os.geteuid() != 0:
        print("🛡️ Elevation required. Re-running with sudo...")
        os.execvp("sudo", ["sudo", "python3"] + sys.argv)

    # 2. Identify Target User Dynamically
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
        uid = pw.pw_uid
    except KeyError:
        print(f"❌ Target user '{target_user}' lookup failed system registration checks.")
        sys.exit(1)

    # Resolve shared permission groups dynamically using the calling user account context
    gid = ensure_group_membership(TARGET_GROUP, [target_user])

    # 3. Path Prep
    source_root = Path(__file__).resolve().parent
    target_root = Path(f"/home/{target_user}/Desktop/{TARGET_FOLDER_NAME}")

    print(f"📂 Source: {source_root}\n📥 Target: {target_root} (User: {target_user}, Group GID: {gid})")

    # 4. Clean and Copy
    if target_root.exists():
        shutil.rmtree(target_root)
    
    target_root.mkdir(parents=True, exist_ok=True)
    
    for item in INCLUDE_ITEMS:
        src = source_root / item
        if src.exists():
            print(f"➡️ Copying {item}...")
            if src.is_dir():
                shutil.copytree(src, target_root / item)
            else:
                shutil.copy2(src, target_root / item)

    # 5. Finalize
    # Copy icon if available
    icon_src = source_root / "web_version_admin/static/assets/CyberKnights_2.png"
    if icon_src.exists():
        print("🎨 Copying icon...")
        shutil.copy2(icon_src, target_root / "icon.png")

    apply_permissions(target_root, uid, gid)
    setup_launcher(target_root.parent, uid, gid)

    print(f"\n✅ Deployment complete to {target_root}")

if __name__ == "__main__":
    main()