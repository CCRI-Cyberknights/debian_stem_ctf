#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
import base64
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class ArchivePasswordFlagGenerator:
    """
    Generator for the Archive Password challenge.
    Embeds real and fake flags into a password-protected ZIP archive.
    """

    def __init__(self, project_root: Path = None, mode="guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")
        
        self.wordlist_template = self.project_root / "flag_generators" / "wordlist.txt"
        self._check_dependencies()
        self.metadata = {}

    @staticmethod
    def _find_project_root() -> Path:
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find .ccri_ctf_root marker.")

    def _check_dependencies(self):
        if not shutil.which("zip"):
            raise RuntimeError("The 'zip' utility is not installed. Run 'apt install zip'.")

    def _run_cmd(self, cmd: list, cwd: Path, description: str):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to {description}:\n{result.stderr.strip()}")

    def _choose_password(self, all_passwords: list) -> str:
        mid = len(all_passwords) // 2
        return random.choice(all_passwords[:mid]) if self.mode == "guided" else random.choice(all_passwords[mid:])

    def _build_payload(self, all_flags: list) -> str:
        flag_list = "\n".join(f"- {flag}" for flag in all_flags)
        return (
            "Mission Debrief:\n\n"
            "Encrypted archive recovered from a CryptKeepers staging machine.\n"
            "Analysis reveals five potential flags, but only one matches the CCRI format.\n\n"
            "Decoded entries:\n"
            f"{flag_list}\n\n"
            "Proceed with caution."
        )

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        challenge_folder.mkdir(parents=True, exist_ok=True)
        
        # 1. Load Wordlist
        if not self.wordlist_template.exists():
            raise FileNotFoundError(f"Missing wordlist template: {self.wordlist_template}")
        all_passwords = self.wordlist_template.read_text().splitlines()
        correct_password = self._choose_password(all_passwords)

        # 2. Files
        wordlist_file = challenge_folder / "wordlist.txt"
        encoded_file = challenge_folder / "message_encoded.txt"
        zip_file = challenge_folder / "secret.zip"

        # Cleanup existing
        for f in [wordlist_file, encoded_file, zip_file]:
            f.unlink(missing_ok=True)

        # 3. Create Payloads
        wordlist_file.write_text("\n".join(all_passwords))
        
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        message_encoded = base64.b64encode(self._build_payload(all_flags).encode()).decode()
        encoded_file.write_text(message_encoded)

        # 4. Zip
        self._run_cmd(
            ["zip", "-j", "-P", correct_password, str(zip_file), str(encoded_file.name)],
            cwd=challenge_folder,
            description="create password-protected zip"
        )
        
        # Cleanup temp file
        encoded_file.unlink()

        # 5. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "last_zip_password": correct_password,
            "challenge_file": str(zip_file.relative_to(self.project_root)),
            "wordlist_file": str(wordlist_file.relative_to(self.project_root)),
            "unlock_method": "Brute-force ZIP password using provided wordlist",
            "hint": "Use wordlist.txt with zip2john + hashcat or fcrackzip.",
        }

        print(f"✅ Archive challenge generated (Pass: {correct_password})")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag