#!/usr/bin/env python3
import shutil
import fnmatch
from pathlib import Path

# === CCRI CTF Environment Cleaner (Pure Pathlib Engine) ===

GITIGNORE_PATH = Path(".gitignore")
TARGET_DIRS = [Path("challenges"), Path("challenges_solo")]
FIREFOX_DIR = Path.home() / ".mozilla" / "firefox"

def load_gitignore_rules(gitignore_path: Path):
    """
    Parses .gitignore into a list of rules using Pathlib.
    Returns a list of tuples: (is_whitelist, pattern)
    """
    rules = []
    if not gitignore_path.is_file():
        print(f"⚠️ Warning: {gitignore_path} not found. Using default unsafe mode (Delete All).")
        return []

    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            is_whitelist = False
            pattern = line
            
            if line.startswith("!"):
                is_whitelist = True
                pattern = line[1:]
            
            # Normalization helper for fnmatch pattern checking
            if pattern.startswith("/"):
                pattern = pattern[1:]
            
            rules.append((is_whitelist, pattern))
    return rules

def should_keep_file(rel_path: str, rules) -> bool:
    """
    Determines if a file path should be preserved based on gitignore logic.
    Iterates all rules sequentially: the last matching rule wins.
    """
    keep = False  # Default to ignoring or deleting because of the baseline '*' rule
    
    for is_whitelist, pattern in rules:
        # Check matching criteria against the pattern and implicit structural wildcards
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(rel_path, f"*{pattern}"):
            keep = is_whitelist
            
    return keep

def clean_directory(base_dir: Path, rules):
    """
    Recursively walks targeted directories via rglob and purges non-whitelisted transient data.
    """
    base_path = base_dir.resolve()
    
    if not base_path.is_dir():
        print(f"⚠️ Directory not found: {base_dir}")
        return

    print(f"Public Scoping Layer: Cleaning target path {base_dir}...")
    
    # Utilizing an un-nested rglob iterator clears files cleanly without os.walk stack frames
    for file_path in base_path.rglob("*"):
        if not file_path.is_file():
            continue
            
        try:
            rel_path = file_path.relative_to(Path.cwd()).as_posix()
        except ValueError:
            # Shield execution context if a target file drifts structurally outside root scope
            continue
        
        # Match file state against tracked rules
        if should_keep_file(rel_path, rules):
            continue
        
        # File is untracked flag data, cache, or generation trash: execute removal
        try:
            file_path.unlink()
            print(f"   🗑️  Deleted: {rel_path}")
        except Exception as e:
            print(f"   ❌ Error deleting tracking target {rel_path}: {e}")

def reset_firefox():
    """
    Clears volatile Firefox browser session metadata, history, and cookies 
    while preserving base release profile boundaries.
    """
    print("Fox-Tail Protocol: Resetting volatile Firefox session storage data...")
    if not FIREFOX_DIR.is_dir():
        print("   ⚠️ Firefox directory context not discovered on host layout. Skipping.")
        return

    # Scan and iterate through standard environment profile releases safely
    for profile in FIREFOX_DIR.glob("*.default-release"):
        print(f"   Cleaning profile destination container: {profile.name}")
        
        # Targeted assets to clear for fresh student attempts without destabilizing the application
        targets = [
            "cookies.sqlite", "places.sqlite", "formhistory.sqlite", 
            "key4.db", "logins.json", "sessionstore.jsonlz4", "webappsstore.sqlite",
            "storage", "cache2", "startupCache"
        ]
        
        for target in targets:
            target_path = profile / target
            try:
                if target_path.is_file():
                    target_path.unlink()
                elif target_path.is_dir():
                    shutil.rmtree(target_path)
            except Exception:
                # Absorb locked resources gracefully if browser threads linger momentarily
                pass
                
    print("   ✅ Volatile browser profile components successfully cleared.")

def main():
    print("==========================================")
    print("      🔄 ENVIRONMENT RESET SCRIPT")
    print("==========================================\n")
    
    # 1. Parse Whitelist Rules
    rules = load_gitignore_rules(GITIGNORE_PATH)
    
    # 2. Clean Challenge Directories
    for target in TARGET_DIRS:
        clean_directory(target, rules)
        
    # 3. Reset Shared Browser States
    reset_firefox()
    
    print("\n✨ Reset Complete. Environment is clean and ready for the next student.")

if __name__ == "__main__":
    main()