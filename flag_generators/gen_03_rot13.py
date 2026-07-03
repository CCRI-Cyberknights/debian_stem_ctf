#!/usr/bin/env python3

from pathlib import Path
import random
import codecs
import sys
from flag_generators.flag_helpers import FlagUtils

class ROT13FlagGenerator:
    """
    Generator for the ROT13 cipher challenge.
    Encodes flags into cipher.txt using ROT13.
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

    @staticmethod
    def rot13(text: str) -> str:
        return codecs.encode(text, "rot_13")

    def _build_payload(self, all_flags: list) -> str:
        """Constructs the mock transmission string."""
        flag_list = "\n".join(f"- {flag}" for flag in all_flags)
        return (
            "Transmission Start\n"
            "------------------------\n"
            "To: CryptKeepers Command Node\n"
            "From: Recon Unit 5\n\n"
            "Flag candidates pulled from intercepted CryptKeepers chatter. "
            "Message scrambled with a simple cipher to slip past basic filters.\n\n"
            "Candidates:\n"
            f"{flag_list}\n\n"
            "Validate and extract the correct CCRI flag.\n\n"
            "Transmission End\n"
            "------------------------\n"
        )

    def write_cipher_file(self, challenge_folder: Path, message: str):
        """Writes the ROT13 encoded payload to disk."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        cipher_file = challenge_folder / "cipher.txt"
        
        try:
            encoded_message = self.rot13(message)
            cipher_file.write_text(encoded_message)
            print(f"📄 Created: {cipher_file.relative_to(self.project_root)}")
        except OSError as e:
            raise RuntimeError(f"Failed to write cipher file: {e}")

    def generate_flag(self, challenge_folder: Path) -> str:
        # 1. Generate Flags
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        # Ensure no duplicates
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()
        
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        # 2. Build and write payload
        message = self._build_payload(all_flags)
        self.write_cipher_file(challenge_folder, message)

        # 3. Store Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(challenge_folder.relative_to(self.project_root) / "cipher.txt"),
            "unlock_method": "ROT13 decode",
            "hint": "Apply ROT13 to cipher.txt to recover plaintext.",
        }

        print(f"✅ Flag generated: {real_flag}")
        return real_flag