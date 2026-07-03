import os
import base64
from pathlib import Path
import config  # Imports localized path logic from the active config module

class Challenge:
    """Represents a single CTF challenge."""

    def __init__(self, id, ch_number, name, folder, flag, script=None, solo_mode=False, has_coach=False):
        self.id = str(id)                 # Force strict string conversion to prevent JSON lookup type-mismatches
        self.ch_number = ch_number        # Challenge number for UI rendering display
        self.name = name                  # Human-readable challenge name
        self.complete = False             # State tracker: defaults to uncompleted
        self.has_coach = has_coach        # Active state flag indicating Coach Mode support

        # === Determine base path via Config using unified Path mechanics ===
        challenges_root = Path(config.SOLO_DIR) if solo_mode else Path(config.GUIDED_DIR)
        
        # Resolve clean, absolute path string targets
        self.folder = str(Path(challenges_root) / folder)

        # Helper scripts are structurally constrained to Guided/Regular tracks
        self.script = str(Path(self.folder) / script) if script else None

        # === Student/Admin mode determines flag decoding ===
        # Runtime validation checks the environmental variable state established by the web hub
        mode = os.environ.get("CCRI_CTF_MODE", "student").lower()
        self.flag = self.decode_flag(flag) if mode == "student" else flag

    def decode_flag(self, encoded_flag: str) -> str:
        """Decode XOR+Base64 encoded flag using the static student key."""
        key = "CTF4EVER"
        try:
            raw = base64.b64decode(encoded_flag)
            # Iterating directly over decoded bytes yields integers natively in Python 3
            return "".join(chr(b ^ ord(key[i % len(key)])) for i, b in enumerate(raw))
        except Exception as e:
            print(f"❌ ERROR decoding student flag: {e}")
            return "[INVALID FLAG]"

    def setComplete(self):
        self.complete = True

    def getId(self):
        return self.id

    def getName(self):
        return self.name

    def getFolder(self):
        return self.folder

    def getScript(self):
        return self.script

    def getFlag(self):
        return self.flag
    
    def getHasCoach(self):
        return self.has_coach

    def __repr__(self):
        return (
            f"#{self.ch_number} {self.name} | ID={self.id} | "
            f"Folder={self.folder} | Script={self.script} | Flag={self.flag} | Coach={self.has_coach}"
        )