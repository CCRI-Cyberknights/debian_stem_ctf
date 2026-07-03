#!/usr/bin/env python3
import sys
import json
from pathlib import Path
import config

# Ensure we can import ChallengeList from BASE_DIR
if str(config.BASE_DIR) not in sys.path:
    sys.path.insert(0, str(config.BASE_DIR))

from ChallengeList import ChallengeList

def load_challenges(mode=None):
    """
    Returns (ChallengeList, challenges_folder_name)
    Tries requested mode, falls back to DEFAULT_MODE, then tries the 'other' mode before failing.
    """
    # Normalize and guard input configurations
    if mode not in ("regular", "solo"):
        mode = config.DEFAULT_MODE

    # If requested mode isn't available, drop back to the environment default
    if mode not in config.AVAILABLE_MODES:
        mode = config.DEFAULT_MODE

    if mode is None:
        raise FileNotFoundError("No configuration mapping matching an available challenge folder discovered.")

    # Convert the core execution base pointer to a robust Path object
    server_base = Path(config.server_dir)

    if mode == "solo":
        challenges_path   = server_base / "challenges_solo.json"
        challenges_folder = "challenges_solo"
        other_mode        = "regular"
        other_path        = server_base / "challenges.json"
    else:
        challenges_path   = server_base / "challenges.json"
        challenges_folder = "challenges"
        other_mode        = "solo"
        other_path        = server_base / "challenges_solo.json"

    print(f"📖 Loading {mode.upper()} challenges from {challenges_path}")

    try:
        # ChallengeList handles path adjustments inside its constructor block smoothly
        challenge_list = ChallengeList(challenges_file=str(challenges_path))
        list_type = "Exploration" if mode == "regular" else "Solo"
        user_type = "Admin" if config.base_mode == "admin" else "Student"
        print(f"✅ {user_type} {list_type} Challenge List loaded ({challenge_list.numOfChallenges} challenges).")
        return challenge_list, challenges_folder
        
    except (FileNotFoundError, json.JSONDecodeError) as err:
        print(f"⚠️ {err.__class__.__name__} encountered during challenge resolution: {err}")
        
        # Try the alternative execution mode fallback if its structure looks healthy
        if other_mode in config.AVAILABLE_MODES and other_path.exists():
            print(f"↪️ Falling back to alternative {other_mode.upper()} array configuration layout.")
            return load_challenges(other_mode)
            
        # Final explicit fallback bubble if both paths fail data integrity validation
        raise RuntimeError(f"❌ Failed to instantiate a valid challenge schema array baseline. Roots checked: {[str(challenges_path), str(other_path)]}") from err