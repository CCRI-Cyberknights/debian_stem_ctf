#!/usr/bin/env python3

from pathlib import Path
import random
import sys
from flag_generators.flag_helpers import FlagUtils

class VigenereFlagGenerator:
    """
    Generator for the Vigenère cipher challenge.
    Encodes an encrypted transmission into cipher.txt.
    """

    DEFAULT_KEY = "login"
    SOLO_KEY = "providence"

    def __init__(self, project_root: Path = None, mode: str = "guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")

        self.vigenere_key = self.DEFAULT_KEY if self.mode == "guided" else self.SOLO_KEY
        self.metadata = {}

    @staticmethod
    def _find_project_root() -> Path:
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find .ccri_ctf_root marker.")

    def _vigenere_encrypt(self, plaintext: str) -> str:
        """Standard Vigenère implementation."""
        result = []
        key = self.vigenere_key.lower()
        key_len = len(key)
        key_indices = [ord(k) - ord('a') for k in key]
        key_pos = 0

        for char in plaintext:
            if char.isalpha():
                offset = ord('A') if char.isupper() else ord('a')
                pi = ord(char) - offset
                ki = key_indices[key_pos % key_len]
                result.append(chr((pi + ki) % 26 + offset))
                key_pos += 1
            else:
                result.append(char)
        return ''.join(result)

    def _build_payload(self, all_flags: list) -> str:
        """Constructs the mock transmission string."""
        flag_list = "\n".join(f"- {flag}" for flag in all_flags)
        return (
            "Transmission Start\n"
            "------------------------\n"
            "To: CryptKeepers Command Node\n"
            "From: Field Unit 7\n\n"
            "Status update: Multiple potential flags recovered while monitoring "
            "CryptKeepers relay traffic. Data has been encoded prior to relay transfer.\n\n"
            "Candidates:\n"
            f"{flag_list}\n\n"
            "Verify the true CCRI flag before submission.\n\n"
            "Transmission End\n"
            "------------------------\n"
        )

    def write_cipher_file(self, challenge_folder: Path, message: str):
        """Writes the encrypted payload to disk."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        cipher_file = challenge_folder / "cipher.txt"
        
        try:
            encrypted_message = self._vigenere_encrypt(message)
            cipher_file.write_text(encrypted_message)
            print(f"📄 Created: {cipher_file.relative_to(self.project_root)}")
        except OSError as e:
            raise RuntimeError(f"Failed to write cipher file: {e}")

    def generate_flag(self, challenge_folder: Path) -> str:
        # 1. Generate Flags
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        # Ensure uniqueness
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
            "vigenere_key": self.vigenere_key,
            "challenge_file": str(challenge_folder.relative_to(self.project_root) / "cipher.txt"),
            "unlock_method": f"Vigenère cipher (key='{self.vigenere_key}')",
            "hint": f"Use the Vigenère key '{self.vigenere_key}' to decrypt cipher.txt.",
        }

        print(f"✅ Flag generated: {real_flag} (Key: {self.vigenere_key})")
        return real_flag