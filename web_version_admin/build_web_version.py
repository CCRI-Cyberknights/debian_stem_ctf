#!/usr/bin/env python3
import json
import base64
import shutil
import stat
import sys
import zipapp
from pathlib import Path

# === CCRI Web Version Builder (Pathlib-Safe Modular Edition) ===

ENCODE_KEY = "CTF4EVER"

def abort(msg):
    print(f"❌ {msg}")
    sys.exit(1)

def xor_encode(plaintext: str, key: str) -> str:
    """XOR + Base64 encode a plaintext flag."""
    return base64.b64encode(
        bytes([ord(c) ^ ord(key[i % len(key)]) for i, c in enumerate(plaintext)])
    ).decode()

def make_scripts_executable(challenges_data, base_dir: Path):
    """Set chmod +x on helper scripts and coach scripts using modern path permissions."""
    print("🔧 Setting executable permissions on scripts...")
    for meta in challenges_data.values():
        challenge_folder = base_dir / "challenges" / Path(meta["folder"]).name
        
        # 1. Handle Exploration Script
        script = meta.get("script")
        if script:
            script_path = challenge_folder / script
            if script_path.is_file():
                try:
                    script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)
                    print(f"   ✅ Executable: {script}")
                except Exception as e:
                    print(f"   ⚠️ Failed to chmod {script}: {e}")
            else:
                print(f"   ⚠️ Missing script: {script_path}")

        # 2. Handle Coach Script (.coach.py) if present
        if meta.get("has_coach"):
            coach_script = ".coach.py"
            coach_path = challenge_folder / coach_script
            if coach_path.is_file():
                try:
                    coach_path.chmod(coach_path.stat().st_mode | stat.S_IXUSR)
                    print(f"   ✅ Executable: {coach_script}")
                except Exception as e:
                    print(f"   ⚠️ Failed to chmod {coach_script}: {e}")

def sanitize_templates(template_dir: Path):
    """Replace Admin Hub text references with dynamic mode selectors inside Jinja wrappers."""
    print("📝 Sanitizing templates for student version...")
    # Use rglob to cleanly match all child templates through deep directory branches
    for html_file in template_dir.rglob("*.html"):
        try:
            content = html_file.read_text(encoding="utf-8")
            sanitized_content = content.replace(
                "CCRI CTF Admin Hub",
                "{{ 'CCRI CTF Admin Hub' if base_mode == 'admin' else 'CCRI CTF Student Hub' }}"
            )
            html_file.write_text(sanitized_content, encoding="utf-8")
            print(f"✅ Sanitized {html_file.name}")
        except Exception as e:
            print(f"⚠️ Failed to sanitize layout file {html_file.name}: {e}")

def _looks_base64(s: str) -> bool:
    try:
        base64.b64decode(s.encode(), validate=True)
        return True
    except Exception:
        return False

def prepare_web_version(base_dir: Path):
    admin_dir   = base_dir / "web_version_admin"
    student_dir = base_dir / "web_version"  # Target asset directory on host file system
    
    # === Core Data Files ===
    admin_json       = admin_dir / "challenges.json"
    solo_json        = admin_dir / "challenges_solo.json"
    templates_folder = admin_dir / "templates"
    static_folder    = admin_dir / "static"

    # === Modular Python Source Framework ===
    required_modules = [
        admin_dir / "server.py",
        admin_dir / "config.py",
        admin_dir / "fake_services.py",
        admin_dir / "routes.py",
        admin_dir / "utils.py",
        admin_dir / "Challenge.py",
        admin_dir / "ChallengeList.py"
    ]

    # === Validate Admin Resource Pre-requisites ===
    print(f"📂 System Target Base Pointer: {base_dir}")
    for p in [admin_json, solo_json] + required_modules:
        if not p.is_file():
            abort(f"Missing required execution resource dependency: {p}")
    for d in (templates_folder, static_folder):
        if not d.is_dir():
            abort(f"Missing required architecture container: {d}")

    # === Clean and Rebuild Distribution Assets Space ===
    if student_dir.exists():
        print("🧹 Purging existing web_version build folder assets...")
        shutil.rmtree(student_dir)
    student_dir.mkdir(parents=True, exist_ok=True)

    # === Process challenges.json (GUIDED TRACK) ===
    print("🔐 Encoding verification flags for student hub (Guided Exploration)...")
    try:
        with open(admin_json, "r", encoding="utf-8") as f:
            admin_data = json.load(f)
    except Exception as e:
        abort(f"Failed to read master challenges matrix: {e}")

    guided_data = {}
    for cid, meta in admin_data.items():
        entry = {
            "name": meta["name"],
            "folder": meta["folder"],
            "flag": xor_encode(meta["flag"], ENCODE_KEY),
        }
        if meta.get("script"):
            entry["script"] = meta["script"]
        if meta.get("has_coach"):
            entry["has_coach"] = meta["has_coach"]
            
        guided_data[cid] = entry

    # Verify and update execution attributes on script endpoints
    make_scripts_executable(admin_data, base_dir)

    guided_json_path = student_dir / "challenges.json"
    with open(guided_json_path, "w", encoding="utf-8") as f:
        json.dump(guided_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Created Guided Framework Matrix: {guided_json_path}")

    # === Process challenges_solo.json (SOLO TRACK) ===
    print("🔐 Encoding verification flags for student hub (Solo Track)...")
    try:
        with open(solo_json, "r", encoding="utf-8") as f:
            admin_solo = json.load(f)
    except Exception as e:
        abort(f"Failed to read solo challenge blueprint data: {e}")

    solo_data = {}
    for cid, meta in admin_solo.items():
        raw_flag = meta.get("real_flag", meta.get("flag"))
        if not raw_flag:
            abort(f"Solo entry {cid} failed integrity check: Missing target flag baseline.")
        entry = {
            "name": meta["name"],
            "folder": meta["folder"],
            "flag": xor_encode(raw_flag, ENCODE_KEY),
        }
        if meta.get("script"):
            entry["script"] = meta["script"]
        if "hint" in meta:
            entry["hint"] = meta["hint"]
        if meta.get("has_coach"):
            entry["has_coach"] = meta["has_coach"]

        solo_data[cid] = entry

    solo_json_path = student_dir / "challenges_solo.json"
    with open(solo_json_path, "w", encoding="utf-8") as f:
        json.dump(solo_data, f, indent=4, ensure_ascii=False)
    print(f"✅ Created Solo Challenge Matrix: {solo_json_path}")

    # === Verify Encoding Schema Validity ===
    for path in (guided_json_path, solo_json_path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        bad = [cid for cid, m in data.items() if not _looks_base64(m.get("flag", ""))]
        if bad:
            abort(f"Data corruption check failed inside {path.name}: Un-obfuscated flag elements discovered: {bad}")
        print(f"🔎 Validated base64 obfuscated integrity checks for: {path.name}")

    # === Copy Asset Layout Packages Into On-Disk Targets ===
    print("📂 Synchronizing display templates and raw static visual packages...")
    shutil.copytree(templates_folder, student_dir / "templates", dirs_exist_ok=True)
    shutil.copytree(static_folder, student_dir / "static", dirs_exist_ok=True)

    # === Sanitize Template Titles dynamically ===
    sanitize_templates(student_dir / "templates")

    # === Build Portable Standalone Zipapp Executable ===
    print("📦 Packing intermediate zipapp source tree configuration...")
    pyz_src = base_dir / "_pyz_src"
    if pyz_src.exists():
        shutil.rmtree(pyz_src)
    pyz_src.mkdir(parents=True, exist_ok=True)

    # Populate module items directly into the distribution compilation bucket
    for module_path in required_modules:
        shutil.copy2(module_path, pyz_src / module_path.name)
        print(f"   - Included backend core node: {module_path.name}")

    # __main__.py: Primary processing handler for the zipapp environment
    main_code = r"""\
import os, sys

def main():
    # Fallback to local on-disk assets directory if explicit override parameters are missing
    if "CCRI_ASSETS_DIR" not in os.environ:
        pyz_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        candidate = os.path.join(pyz_dir, "web_version")
        if os.path.isdir(candidate):
            os.environ["CCRI_ASSETS_DIR"] = candidate

    os.environ.setdefault("CCRI_CTF_MODE", "student")

    import config
    import fake_services
    import server

    # Boot the simulated capture engines cleanly in the background threads
    fake_services.start_all_services(config.AVAILABLE_MODES)

    print(f"📖 Using template folder at: {server.app.template_folder}")
    print(f"🧰 Static folder at: {server.app.static_folder}")
    print(f"🚀 {os.environ['CCRI_CTF_MODE'].capitalize()} Hub running on http://127.0.0.1:5000")
    
    server.app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    main()
"""
    with open(pyz_src / "__main__.py", "w", encoding="utf-8") as f:
        f.write(main_code)

    # Package and sign the finished executable zipapp capsule at root level
    pyz_path = base_dir / "ccri_ctf.pyz"
    if pyz_path.exists():
        pyz_path.unlink()
        
    zipapp.create_archive(str(pyz_src), str(pyz_path), interpreter="/usr/bin/env python3")
    print(f"🎁 Built portable platform application zipapp binary: {pyz_path}")
    print("👉 Launch verification node locally with: python3 " + pyz_path.name)

    # Clean up compilation directory artifacts
    if pyz_src.exists():
        shutil.rmtree(pyz_src)

    print("\n🎉 Student web_version build completed successfully!\n")

def main():
    print("🚀 Starting Web Version Build Process (Modular Auto-Compile)...")
    
    # 🛠️ UPDATED PATH LOGIC:
    # Since the script lives in 'web_version_admin', going up 2 parent levels 
    # maps perfectly to the main 'debian_stem_ctf' root folder.
    base_dir = Path(__file__).resolve().parent.parent
    
    prepare_web_version(base_dir)
    print("✅ Build process finished successfully.")
    input("\n📖 Press ENTER to exit compile interface...")

if __name__ == "__main__":
    main()
