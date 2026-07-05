#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import pwd
from pathlib import Path

# === Configuration ===
TARGET_FOLDER_NAME = "ctf_takehome"

INCLUDE_ITEMS = [
    "challenges", "challenges_solo", "web_version", "ccri_ctf.pyz",
    "stop_web_hub.py", ".ccri_ctf_root",
    "coach_core.py", "worker_node.py", "exploration_core.py", "reset_environment.py"
]

def apply_permissions(path: Path, uid: int, gid: int):
    """Recursively applies correct ownership and permissions."""
    def is_script(fname): return fname.endswith((".py", ".sh", ".desktop", ".pyz", ".command"))

    os.chown(path, uid, gid)
    os.chmod(path, 0o755)

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

def generate_launcher(launcher_dst: Path, target_user: str):
    """Generates the .desktop file with an absolute icon path."""
    work_dir = f"$HOME/Desktop/{TARGET_FOLDER_NAME}"
    absolute_icon = f"/home/{target_user}/Desktop/{TARGET_FOLDER_NAME}/icon.png"
    
    content = (
        "[Desktop Entry]\nVersion=1.0\nType=Application\nTerminal=true\n"
        "Name=Launch CCRI CTF Hub (Take-Home)\n"
        f"Exec=bash -c 'cd \"{work_dir}\" && python3 start_web_hub.py'\n"
        f"Icon={absolute_icon}\n"
        "Comment=Start the CyberKnights Challenge Hub\n"
    )
    launcher_dst.write_text(content, encoding="utf-8")

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (sudo) to manage file ownership.")
        sys.exit(1)

    source_root = Path(__file__).resolve().parent
    
    target_user = os.environ.get("SUDO_USER")
    if not target_user:
        file_uid = Path(__file__).resolve().stat().st_uid
        if file_uid != 0:
            target_user = pwd.getpwuid(file_uid).pw_name
        else:
            print("❌ Could not automatically determine the target user.")
            sys.exit(1)

    try:
        pw_record = pwd.getpwnam(target_user)
        uid, gid = pw_record.pw_uid, pw_record.pw_gid
    except KeyError:
        print(f"❌ Target user '{target_user}' lookup failed.")
        sys.exit(1)

    target_root = Path(f"/home/{target_user}/Desktop/{TARGET_FOLDER_NAME}")
    print(f"📂 Source: {source_root}\n📥 Target: {target_root} (User: {target_user})")

    target_root.mkdir(parents=True, exist_ok=True)
    if not (source_root / ".ccri_ctf_root").exists():
        (source_root / ".ccri_ctf_root").touch()

    # Copy files
    for item in INCLUDE_ITEMS:
        src = source_root / item
        if src.exists():
            print(f"➡️ Copying {item}...")
            safe_copy(src, target_root / item)
        else:
            print(f"⚠️ Skipping missing item: {item}")

    # Download Offline Wheels Cache
    wheels_dst = target_root / "wheels"
    wheels_dst.mkdir(parents=True, exist_ok=True)
    print("📦 Downloading offline dependency wheelhouse cache...")
    try:
        # Uses the parent workspace environment to download the packages cleanly
        subprocess.run([
            "/home/stemctf/Desktop/debian_stem_ctf/.venv/bin/pip", "download", 
            "-d", str(wheels_dst), "flask", "requests", "markdown"
        ], check=True)
    except Exception as e:
        print(f"❌ Failed to cache wheels offline: {e}")
        sys.exit(1)

    # Icon Handling
    icon_src = source_root / "web_version_admin/static/assets/CyberKnights_2.png"
    if icon_src.exists():
        print("🎨 Copying icon...")
        shutil.copy2(icon_src, target_root / "icon.png")

    # Finalize Permissions & Launcher
    print("🔒 Setting permissions and generating launcher...")
    
    # Write customized offline bootstrapping launcher script
    generate_bootstrap_start_script(target_root / "start_web_hub.py")
    
    apply_permissions(target_root, uid, gid)
    
    # Pass target_user down to resolve the absolute icon path path cleanly
    launcher = target_root / "Launch_CCRI_CTF_HUB.desktop"
    generate_launcher(launcher, target_user)
    os.chown(launcher, uid, gid) 
    
    try:
        subprocess.run(["gio", "set", str(launcher), "metadata::trusted", "true"], check=False)
    except Exception:
        pass

    print(f"\n✅ Take-home version deployed with offline wheelhouse cache at {target_root}")

def generate_bootstrap_start_script(dst_path: Path):
    """Generates an offline-ready start_web_hub.py file for students."""
    code = '''#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def main():
    base_dir = Path(__file__).resolve().parent
    venv_dir = base_dir / ".venv"
    wheels_dir = base_dir / "wheels"

    if not venv_dir.exists():
        print("📦 Initializing localized offline challenge runtime engine...")
        try:
            subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
            pip_path = venv_dir / "bin" / "pip"
            
            print("🚚 Installing dependencies from offline wheelhouse...")
            subprocess.run([
                str(pip_path), "install", "--no-index", 
                "--find-links", str(wheels_dir), 
                "flask", "requests", "markdown"
            ], check=True)
            print("✅ Runtime engine successfully provisioned offline.")
        except Exception as e:
            print(f"❌ Critical Error during offline environment creation: {e}")
            sys.exit(1)

    venv_python = venv_dir / "bin" / "python3"
    zipapp_path = base_dir / "ccri_ctf.pyz"
    
    if not zipapp_path.exists():
        print("❌ Error: ccri_ctf.pyz platform execution binary is missing.")
        sys.exit(1)
        
    print("🌐 Launching training hub browser window...")
    try:
        subprocess.Popen(
            ["bash", "-c", "sleep 1.5 && xdg-open http://127.0.0.1:5000"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

    os.execv(str(venv_python), [str(venv_python), str(zipapp_path)])

if __name__ == "__main__":
    main()
'''
    dst_path.write_text(code, encoding="utf-8")

if __name__ == "__main__":
    main()
