#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class MetadataFlagGenerator:
    """
    Generator for the Metadata challenge.
    Embeds real and fake flags into EXIF metadata of capybara.jpg.
    """

    def __init__(self, project_root: Path = None, mode="guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")
        
        self.generator_dir = Path(__file__).parent.resolve()
        self.source_image = self.generator_dir / "capybara.jpg"
        
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
        if not shutil.which("exiftool"):
            raise RuntimeError("The 'exiftool' utility is not installed. Run 'apt install libimage-exiftool-perl'.")

    def _run_cmd(self, cmd: list, description: str):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to {description}:\n{result.stderr.strip()}")

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Copies image and embeds all flags into EXIF tags in a single pass."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        dest_image = challenge_folder / "capybara.jpg"
        
        # 1. Copy source
        if not self.source_image.exists():
            raise FileNotFoundError(f"Source image missing: {self.source_image}")
        dest_image.write_bytes(self.source_image.read_bytes())

        # 2. Prepare Metadata Tags
        random.shuffle(fake_flags)
        tags = {
            "ImageDescription": fake_flags[0],
            "Artist": fake_flags[1],
            "Copyright": fake_flags[2],
            "XPKeywords": fake_flags[3],
            "UserComment": real_flag
        }

        # 3. Build single exiftool command
        # -overwrite_original prevents creation of _original files
        cmd = ["exiftool", "-overwrite_original"]
        for tag, val in tags.items():
            cmd.append(f"-{tag}={val}")
        cmd.append(str(dest_image))

        self._run_cmd(cmd, "embed EXIF metadata")
        print(f"📝 Embedded metadata tags into {dest_image.name}")

        # 4. Save Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(dest_image.relative_to(self.project_root)),
            "unlock_method": "Inspect EXIF metadata of capybara.jpg to find the flag",
            "hint": "Use exiftool or exifread to view metadata tags."
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        # Ensure exactly 4 unique fake flags
        fake_set = set()
        while len(fake_set) < 4:
            fake_set.add(FlagUtils.generate_fake_flag())
        fake_flags = list(fake_set)

        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag