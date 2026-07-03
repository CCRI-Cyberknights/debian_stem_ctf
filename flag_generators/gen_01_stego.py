#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class StegoFlagGenerator:
    """
    Generator for the Stego challenge flags.
    Handles embedding, metadata, and cleanup with strict error checking.
    """

    def __init__(self, project_root: Path = None, mode: str = "guided"):
        self.project_root = project_root or self._find_project_root()
        self.generator_dir = self.project_root / "flag_generators"
        self.source_image = self.generator_dir / "squirrel.jpg"
        self.mode = mode.lower()

        if self.mode not in ["guided", "solo"]:
            raise ValueError(f"Invalid mode '{self.mode}'. Expected 'guided' or 'solo'.")

        # Verify system environment immediately
        self._check_dependencies()

        self.last_password = None
        self.metadata = {}

    @staticmethod
    def _find_project_root() -> Path:
        """Locates the project root by searching for the .ccri_ctf_root marker."""
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find project root marker (.ccri_ctf_root).")

    def _check_dependencies(self):
        """Fail-fast: Ensure required CLI tools are present."""
        for tool in ["steghide", "exiftool"]:
            if not shutil.which(tool):
                print(f"❌ CRITICAL ERROR: '{tool}' not found. Please install via 'apt install {tool}'.")
                sys.exit(1)

    def _run_cmd(self, cmd: list, description: str):
        """Helper to wrap subprocess calls with logging."""
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to {description}:\n{result.stderr.strip()}")
        return result

    def write_password_metadata(self, image_path: Path, passphrase: str):
        """Embeds a mode-specific hint into JPEG metadata."""
        comment = (
            f"Guided hint: steghide passphrase is '{passphrase}'." 
            if self.mode == "guided" 
            else f'CryptKeepers whisper the key: "{passphrase}".'
        )
        
        self._run_cmd(
            ["exiftool", "-overwrite_original", f"-UserComment={comment}", str(image_path)],
            "embed metadata"
        )
        print("📝 Embedded password hint into JPEG metadata.")

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list, passphrase: str):
        dest_image = challenge_folder / "squirrel.jpg"
        hidden_file = challenge_folder / "hidden_flags.txt"

        if not self.source_image.exists():
            raise FileNotFoundError(f"Source image missing: {self.source_image}")

        # Ensure folder exists
        challenge_folder.mkdir(parents=True, exist_ok=True)
        
        # Copy image
        dest_image.write_bytes(self.source_image.read_bytes())
        
        # Prepare hidden payload
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        hidden_file.write_text("\n".join(all_flags))

        try:
            # Embed
            self._run_cmd(
                ["steghide", "embed", "-cf", str(dest_image), "-ef", str(hidden_file), "-p", passphrase],
                "embed secret data with steghide"
            )
            print(f"✅ Steghide embedding complete.")
            
            # Metadata
            self.write_password_metadata(dest_image, passphrase)
        finally:
            if hidden_file.exists():
                hidden_file.unlink()
                print("🗑️ Cleaned up temporary files.")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        self.last_password = "password" if self.mode == "guided" else "ckeepers"

        # Embed logic
        self.embed_flags(challenge_folder, real_flag, fake_flags, self.last_password)
        
        print(f"✅ {self.mode.capitalize()} mode generated.")
        return real_flag