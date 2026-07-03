import os
import sys
import json
from pathlib import Path

def find_project_root() -> Path:
    """Finds the root by looking for .ccri_ctf_root marker."""
    curr = Path(__file__).resolve().parent
    for parent in [curr] + list(curr.parents):
        if (parent / ".ccri_ctf_root").exists():
            return parent
    print("❌ ERROR: Could not find .ccri_ctf_root", file=sys.stderr)
    sys.exit(1)

def get_ctf_mode() -> str:
    """Detects current mode from environment variable."""
    return os.environ.get("CCRI_MODE", "guided")

def load_unlock_data(project_root: Path, challenge_id: str) -> dict:
    """Loads metadata specific to the challenge ID."""
    mode = get_ctf_mode()
    filename = "validation_unlocks_solo.json" if mode == "solo" else "validation_unlocks.json"
    path = project_root / "web_version_admin" / filename
    
    if not path.exists():
        print(f"❌ Unlock file missing: {path}", file=sys.stderr)
        sys.exit(1)
        
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get(challenge_id, {})

def load_flag(project_root: Path, challenge_id: str) -> str:
    """Retrieves the real flag for comparison."""
    return load_unlock_data(project_root, challenge_id).get("real_flag", "")

def get_challenge_file(project_root: Path, challenge_id: str, unlock_data: dict) -> Path:
    """Resolves the challenge file path using generated metadata."""
    # Prioritize the exact path saved by the generator in metadata
    file_rel = unlock_data.get("challenge_file")
    
    if file_rel:
        return project_root / file_rel
    
    # Fallback to standard convention
    mode = get_ctf_mode()
    base_dir = "challenges_solo" if mode == "solo" else "challenges"
    return project_root / base_dir / challenge_id / "encoded.txt"