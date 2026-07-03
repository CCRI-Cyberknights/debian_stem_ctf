#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
import hashlib
import base64
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class HashcatFlagGenerator:
    """
    Generator for the Hashcat challenge.
    Splits flags into parts, encodes them, and creates password-protected zips.
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

    def _md5_hash(self, password: str) -> str:
        return hashlib.md5(password.encode("utf-8")).hexdigest()

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        challenge_folder.mkdir(parents=True, exist_ok=True)
        segments_dir = challenge_folder / "segments"
        segments_dir.mkdir(exist_ok=True)

        # 1. Prepare Data
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        # Split flags into 3 segments
        parts = []
        for flag in all_flags:
            split_parts = flag.replace("-", " ").split()
            if len(split_parts) < 3:
                split_parts += ["XXXX"] * (3 - len(split_parts))
            parts.append(split_parts[:3])

        # Transpose parts
        part1 = [p[0] for p in parts]
        part2 = [p[1] for p in parts]
        part3 = [p[2] for p in parts]

        # 2. Files Setup
        if not self.wordlist_template.exists():
            raise FileNotFoundError(f"Missing wordlist template: {self.wordlist_template}")
        
        all_passwords = self.wordlist_template.read_text().splitlines()
        chosen_passwords = random.sample(all_passwords, 3)
        
        hashes_txt = challenge_folder / "hashes.txt"
        wordlist_file = challenge_folder / "wordlist.txt"
        
        # Cleanup
        wordlist_file.unlink(missing_ok=True)
        hashes_txt.unlink(missing_ok=True)
        
        # 3. Create segments and hashes
        hash_password_zip_map = {}
        hash_lines = []

        for idx, (password, segment) in enumerate(zip(chosen_passwords, [part1, part2, part3]), start=1):
            # Encode segment
            encoded_text = "\n".join(segment)
            encoded_b64 = base64.b64encode(encoded_text.encode()).decode()
            temp_file = challenge_folder / f"encoded_segments{idx}.txt"
            temp_file.write_text(encoded_b64)

            # Zip
            zip_file = segments_dir / f"part{idx}.zip"
            zip_file.unlink(missing_ok=True)
            self._run_cmd(
                ["zip", "-j", "-P", password, str(zip_file), str(temp_file.name)],
                cwd=challenge_folder,
                description=f"zip part {idx}"
            )
            temp_file.unlink()

            # Hash
            hash_val = self._md5_hash(password)
            hash_lines.append(hash_val)
            hash_password_zip_map[hash_val] = {
                "password": password,
                "zip_file": str(zip_file.relative_to(self.project_root))
            }

        # Write support files
        hashes_txt.write_text("\n".join(hash_lines))
        wordlist_file.write_text("\n".join(all_passwords))

        # 4. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "reconstructed_flag": real_flag,
            "challenge_files": {
                "hashes": str(hashes_txt.relative_to(self.project_root)),
                "wordlist": str(wordlist_file.relative_to(self.project_root)),
                "segments_dir": str(segments_dir.relative_to(self.project_root)),
            },
            "hash_password_zip_map": hash_password_zip_map,
            "unlock_method": "Recover MD5 hashes with Hashcat and unzip protected parts",
            "hint": "Use hashes.txt + wordlist.txt with Hashcat to crack passwords and extract ZIPs."
        }
        print(f"✅ Hashcat challenge generated.")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag