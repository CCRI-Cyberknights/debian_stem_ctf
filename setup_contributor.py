#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse
import shlex
import shutil
import stat
from pathlib import Path

# ==============================================================================
# 🎛️ DUAL-COMPATIBILITY CONTEXT ENGINE
# ==============================================================================
# Detect if the script is being executed directly via an internet pipe (curl)
IS_PIPED = "__file__" not in globals() or __file__ == "<stdin>" or not os.path.exists(__file__)

if IS_PIPED:
    # Handle curl execution: fall back to evaluating active path layout rules
    if Path.cwd().name == "debian_stem_ctf":
        REPO_ROOT = Path.cwd()
    else:
        REPO_ROOT = Path.cwd() / "debian_stem_ctf"
else:
    # Handle standard clone execution: locate native file parent coordinates
    REPO_ROOT = Path(__file__).resolve().parent

# ==============================================================================

APT_ENV = {
    **os.environ,
    "DEBIAN_FRONTEND": "noninteractive",
    "NEEDRESTART_SUSPEND": "1",
    "UCF_FORCE_CONFOLD": "1",
}

def run(cmd, check=True, env=None):
    if isinstance(cmd, str):
        print(f"💻 Running: {cmd}")
        result = subprocess.run(cmd, shell=True, env=env or APT_ENV)
    else:
        print(f"💻 Running: {' '.join(shlex.quote(c) for c in cmd)}")
        result = subprocess.run(cmd, env=env or APT_ENV)
    if check and result.returncode != 0:
        print(f"❌ ERROR: Command failed -> {cmd}", file=sys.stderr)
        sys.exit(1)
    return result.returncode

def apt_update():
    run(["sudo", "-E", "apt-get", "update", "-y"])

def apt_install_packages(packages):
    print("📦 Installing system dependencies (non-interactive)...")
    apt_update()
    base_cmd = [
        "sudo", "-E", "apt-get", "install", "-yq",
        "-o", 'Dpkg::Options::=--force-confdef',
        "-o", 'Dpkg::Options::=--force-confold',
    ]
    run(base_cmd + packages)

# ---------- Wireshark / dumpcap ----------
def ensure_group(name):
    rc = run(["getent", "group", name], check=False)
    if rc != 0:
        run(["sudo", "groupadd", "--system", name], check=False)

def add_users_to_group(group, users):
    for u in users:
        if not u:
            continue
        rc = run(["id", u], check=False)
        if rc == 0:
            run(["sudo", "usermod", "-aG", group, u], check=False)

def is_setuid(path):
    try:
        st = os.stat(path)
        return bool(st.st_mode & stat.S_ISUID)
    except FileNotFoundError:
        return False

def getcap(path):
    try:
        out = subprocess.check_output(["getcap", path], text=True).strip()
        return out
    except Exception:
        return ""

def ensure_dumpcap_nonroot():
    dumpcap = shutil.which("dumpcap")
    if not dumpcap:
        print("ℹ️ dumpcap not found; skipping perms setup.")
        return

    run(["sudo", "setcap", "cap_net_raw,cap_net_admin+eip", dumpcap], check=False)
    caps = getcap(dumpcap)
    if "cap_net_admin,cap_net_raw" in caps and "eip" in caps:
        print(f"✅ dumpcap caps OK: {caps}")
        return

    run("echo 'wireshark-common wireshark-common/install-setuid boolean true' | sudo debconf-set-selections", check=False)
    run(["sudo", "dpkg-reconfigure", "-f", "noninteractive", "wireshark-common"], check=False)
    if is_setuid(dumpcap):
        print(f"✅ dumpcap setuid OK: {dumpcap}")
        return

    local_dump = "/usr/local/bin/dumpcap"
    run(["sudo", "install", "-o", "root", "-g", "wireshark", "-m", "0750", dumpcap, local_dump], check=False)
    run(["sudo", "chmod", "u+s", local_dump], check=False)
    use_path = shutil.which("dumpcap") or local_dump
    print(f"🛠 Using dumpcap at: {use_path}")

def preseed_wireshark_and_install():
    print("🧪 Preseeding Wireshark (allow non-root capture) and installing non-interactively...")
    preseed = 'wireshark-common wireshark-common/install-setuid boolean true'
    run(f"echo '{preseed}' | sudo debconf-set-selections")
    apt_install_packages(["wireshark", "wireshark-common", "tshark", "libcap2-bin"])
    ensure_group("wireshark")
    env_user = os.environ.get("SUDO_USER") or os.environ.get("USER") or ""
    add_users_to_group("wireshark", [env_user, "user"])

# ---------- Python / pip Virtual Environment ----------
def pip_install():
    print("🐍 Creating isolated virtual environment...")
    venv_dir = REPO_ROOT / ".venv"
    
    run(["python3", "-m", "venv", str(venv_dir)])
    venv_pip = venv_dir / "bin" / "pip"
    
    print("📚 Installing Flask, MarkupSafe, Requests and Markdown safely inside the venv...")
    run([str(venv_pip), "install", "--upgrade", "pip"])
    run([str(venv_pip), "install", "flask", "markupsafe", "requests", "markdown"])

# ---------- zsteg ----------
def install_zsteg():
    print("💎 Installing Ruby and zsteg...")
    apt_install_packages(["ruby", "ruby-dev", "libmagic-dev"])
    run(["sudo", "gem", "install", "zsteg", "--no-document"])

# ---------- CyberChef (offline) ----------
def install_cyberchef_offline():
    print("🧁 Installing offline CyberChef + desktop entry...")
    apt_install_packages(["curl", "xdg-utils", "desktop-file-utils"])
    CYBER_DIR = "/opt/cyberchef"
    run(["sudo", "mkdir", "-p", CYBER_DIR])
    if not os.path.exists(f"{CYBER_DIR}/index.html") or os.path.getsize(f"{CYBER_DIR}/index.html") == 0:
        run(["sudo", "curl", "-fsSL", "https://gchq.github.io/CyberChef/", "-o", f"{CYBER_DIR}/index.html"], check=False)
    desktop_entry = """[Desktop Entry]
Type=Application
Name=CyberChef (Offline)
Exec=xdg-open file:///opt/cyberchef/index.html
Icon=utilities-terminal
Terminal=false
Categories=Utility;Education;Development;
"""
    run(["bash", "-lc", f"printf %s {shlex.quote(desktop_entry)} | sudo tee /usr/share/applications/cyberchef.desktop >/dev/null"])
    run(["bash", "-lc", "command -v update-desktop-database >/dev/null && sudo update-desktop-database || true"], check=False)

# ---------- Helpers for john/*2john parity ----------
def ensure_john_and_helpers_on_path():
    print("🧰 Ensuring john/*2john helpers are in PATH...")
    for cand in ("/usr/sbin/john", "/usr/bin/john"):
        if os.path.exists(cand) and os.access(cand, os.X_OK):
            run(["sudo", "ln", "-sf", cand, "/usr/local/bin/john"], check=False)
            break
    for root in ("/usr/sbin",):
        if os.path.isdir(root):
            for name in os.listdir(root):
                if name.endswith("2john"):
                    src = os.path.join(root, name)
                    if os.access(src, os.X_OK):
                        run(["sudo", "ln", "-sf", src, f"/usr/local/bin/{name}"], check=False)
    share = "/usr/share/john"
    if os.path.isdir(share):
        for name in os.listdir(share):
            if name.endswith("2john") or name.endswith("2john.py"):
                src = os.path.join(share, name)
                dst = f"/usr/local/bin/{name}"
                if os.access(src, os.X_OK):
                    run(["sudo", "ln", "-sf", src, dst], check=False)
                else:
                    wrapper = f"""#!/usr/bin/env bash
exec python3 "{src}" "$@"
"""
                    run(["bash", "-lc", f"printf %s {shlex.quote(wrapper)} | sudo tee {shlex.quote(dst)} >/dev/null"])
                    run(["sudo", "chmod", "+x", dst], check=False)

# ---------- Git ----------
def get_git_config(key):
    res = subprocess.run(["git", "config", "--global", key], capture_output=True, text=True)
    return res.stdout.strip() if res.returncode == 0 else None

def configure_git(git_name=None, git_email=None):
    print("\n🔧 Checking Git configuration...")
    if get_git_config("user.name") and get_git_config("user.email"):
        return
    if not git_name: git_name = os.environ.get("GIT_NAME")
    if not git_email: git_email = os.environ.get("GIT_EMAIL")
    
    if git_name and git_email:
        run(["git", "config", "--global", "user.name", git_name])
        run(["git", "config", "--global", "user.email", git_email])
        run(["git", "config", "--global", "credential.helper", "store"])
        print("✅ Git configuration saved.")
    else:
        print("⚠️  Skipping Git prompts (non-interactive).")

# ---------- XFCE Styling Engine ----------
def configure_xfce_cyber_theme():
    print("🎨 Sculpting the XFCE desktop layout into a security profile...")
    run(["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/position", "-s", "p=6;x=0;y=0"], check=False)
    run(["xfconf-query", "-c", "xfce4-panel", "-p", "/panels/panel-1/length", "-s", "100"], check=False)
    run(["xfconf-query", "-c", "xfce4-terminal", "-p", "/background-darkness", "-n", "-t", "double", "-s", "0.95"], check=False)
    print("✅ XFCE workspace structural layout adjusted.")

# ---------- Desktop Launcher Setup ----------
def setup_desktop_launcher():
    print("📎 Configuring desktop launcher for Main Repo...")
    icon_path = REPO_ROOT / "web_version_admin" / "static" / "assets" / "CyberKnights_2.png"
    launcher_path = REPO_ROOT / "Launch_CCRI_CTF_HUB.desktop"

    final_icon = str(icon_path) if icon_path.exists() else "utilities-terminal"
    
    content = f"""[Desktop Entry]
Version=1.0
Type=Application
Terminal=true
Name=Launch_CCRI_CTF_Hub
Exec=bash -c "cd {REPO_ROOT} && .venv/bin/python3 start_web_hub.py"
Icon={final_icon}
Name[en_US]=Launch_CCRI_CTF_Hub
Comment=Launch the Dev Environment for CCRI CTF
Categories=Utility;
"""
    try:
        with open(launcher_path, "w") as f:
            f.write(content)
        os.chmod(launcher_path, 0o755)
        
        # Resolve real system owner properties safely based on the repo root folder path
        st = os.stat(REPO_ROOT)
        uid = st.st_uid
        gid = st.st_gid
        os.chown(launcher_path, uid, gid)
        print("✅ Launcher updated to target sandbox venv interpreter.")
    except Exception as e:
        print(f"⚠️  Could not update launcher: {e}")

# ---------- CLI ----------
def parse_args():
    p = argparse.ArgumentParser(description="CCRI CyberKnights environment setup")
    p.add_argument("--git-name", help="Git user.name (non-interactive)")
    p.add_argument("--git-email", help="Git user.email (non-interactive)")
    return p.parse_args()

def main():
    args = parse_args()

    print("\n🚀 Setting up your CCRI_CTF contributor environment...")
    print("=" * 60 + "\n")

    preseed_wireshark_and_install()
    ensure_dumpcap_nonroot()

    apt_packages = [
        "git", "python3", "python3-pip", "python3-venv", "gcc", "build-essential",
        "fonts-noto-color-emoji",
        "python3-markdown", "python3-scapy",
        "curl", "lsof", "xdg-utils", "libglib2.0-bin",
        "xfce4-terminal", "xfce4-goodies",
        "exiftool", "zbar-tools", "hashcat", "unzip", "steghide",
        "nmap", "qrencode", "vim-common", "util-linux",
        "binwalk", "fcrackzip", "john", "imagemagick", "hexedit", "feh",
        "p7zip-full", "ncat", "xxd", "tmux",
    ]
    apt_install_packages(apt_packages)

    # Automatically clone the core repository code if executed via curl pipe sequence
    if IS_PIPED and not REPO_ROOT.exists():
        print("📥 Piped execution detected and repository missing. Cloning main repository automatically...")
        run(["git", "clone", "https://github.com/CCRI-Cyberknights/debian_stem_ctf.git", str(REPO_ROOT)])

    ensure_john_and_helpers_on_path()
    install_cyberchef_offline()
    pip_install()
    install_zsteg()
    configure_git(args.git_name, args.git_email)
    configure_xfce_cyber_theme()
    setup_desktop_launcher()

    print("\n✅ Base environment ready.")
    print("   • Admin run (dev):   .venv/bin/python3 web_version_admin/server.py")
    print("   • Student run:       .venv/bin/python3 ccri_ctf.pyz")
    print("   • Desktop launcher:  Updated with custom icon! Double-click to run.")
    print("\n🎉 Setup complete!")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️  This script may perform privileged operations via sudo.")
    main()
