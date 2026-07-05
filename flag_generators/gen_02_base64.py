#!/usr/bin/env python3

import base64
import random
import sys
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class Base64FlagGenerator:
    """
    Generator for the Base64 intercepted message challenge.
    Encodes an intercepted transmission into encoded.txt.
    """

    def __init__(self, project_root: Path = None, mode: str = "guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")
        
        self.metadata = {}

    @staticmethod
    def _find_project_root() -> Path:
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find .ccri_ctf_root marker.")

    def _build_payload(self, all_flags: list) -> str:
        """Constructs the mock transmission string."""
        flag_list = "\n".join(f"- {flag}" for flag in all_flags)
        return (
            "Transmission Start\n"
            "------------------------\n"
            "To: CryptKeepers Command Node\n"
            "From: Field Operative 4\n\n"
            "Flag candidates recovered from a CryptKeepers data drop during network sweep. "
            "Message encoded to avoid casual inspection.\n\n"
            "Candidates:\n"
            f"{flag_list}\n\n"
            "Verify and submit the authentic CCRI flag.\n\n"
            "Transmission End\n"
            "------------------------\n"
        )

    def write_encoded_file(self, challenge_folder: Path, message: str):
        """Writes the Base64 encoded payload to disk."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        encoded_file = challenge_folder / "encoded.txt"
        
        try:
            encoded_message = base64.b64encode(message.encode("utf-8")).decode("utf-8")
            encoded_file.write_text(encoded_message + "\n")
            print(f"📄 Created: {encoded_file.relative_to(self.project_root)}")
        except OSError as e:
            raise RuntimeError(f"Failed to write encoded file: {e}")

    def generate_flag(self, challenge_folder: Path) -> str:
        # 1. Generate Flags
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = FlagUtils.generate_batch(4, is_real=False)
        
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        # 2. Build and write payload
        message = self._build_payload(all_flags)
        self.write_encoded_file(challenge_folder, message)

        # 3. Store Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(challenge_folder.relative_to(self.project_root) / "encoded.txt"),
            "unlock_method": "Base64 decode",
            "hint": "Decode encoded.txt using base64 -d or an online tool.",
        }

        print(f"✅ Flag generated: {real_flag}")
        return real_flag