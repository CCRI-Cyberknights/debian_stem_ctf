#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class QRCodeFlagGenerator:
    """
    Generator for the QR Codes challenge.
    Produces QR code PNGs with 1 real flag and 4 decoys.
    """

    def __init__(self, project_root: Path = None, mode="guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")
        
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
        if not shutil.which("qrencode"):
            raise RuntimeError("The 'qrencode' utility is not installed. Run 'apt install qrencode'.")

    def _run_cmd(self, cmd: list, description: str):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to {description}:\n{result.stderr.strip()}")

    def _clean_qr_codes(self, folder: Path):
        """Remove existing qr_*.png files to ensure a clean build."""
        for qr_file in folder.glob("qr_*.png"):
            qr_file.unlink(missing_ok=True)
        print(f"🗑️ Cleaned old QR codes in {folder.name}")

    def embed_flags_as_qr(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Generates 5 QR codes (1 real, 4 fake) in the challenge folder."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        self._clean_qr_codes(challenge_folder)

        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        for i, flag in enumerate(all_flags, start=1):
            qr_file = challenge_folder / f"qr_{i:02}.png"
            # Using -s 6 for a decent output size (scale)
            self._run_cmd(
                ["qrencode", "-o", str(qr_file), "-s", "6", flag],
                description=f"generate QR code {i}"
            )
            print(f"📸 Created {qr_file.name}")

        # Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_folder": str(challenge_folder.relative_to(self.project_root)),
            "unlock_method": "Scan QR codes to reveal flags and find the real one",
            "hint": "Use a QR scanner app or zbarimg to read qr_*.png"
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        # Ensure uniqueness
        fake_set = set()
        while len(fake_set) < 4:
            fake_set.add(FlagUtils.generate_fake_flag())
        fake_flags = list(fake_set)
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags_as_qr(challenge_folder, real_flag, fake_flags)
        return real_flag