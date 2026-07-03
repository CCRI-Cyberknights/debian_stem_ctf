#!/usr/bin/env python3

import sys
import os
import random
from pathlib import Path
from typing import List, Tuple
from flag_generators.flag_helpers import FlagUtils

class HexHuntingFlagGenerator:
    """
    Generator for the Hex Hunting challenge.
    Embeds real and fake flags into a random binary file.
    """

    def __init__(self, project_root: Path = None, mode="guided"):
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

    def _get_offsets(self, bin_size: int, spans: List[int]) -> List[int]:
        """Finds non-overlapping offsets for flag placement."""
        max_start = bin_size - max(spans) - 1
        chosen: List[Tuple[int, int]] = []
        offsets: List[int] = []

        for span in spans:
            for _ in range(10_000):
                s = random.randint(100, max_start)
                e = s + span - 1
                if any(not (e < a or s > b) for a, b in chosen):
                    continue
                chosen.append((s, e))
                offsets.append(s)
                break
            else:
                raise RuntimeError("❌ Could not find non-overlapping offsets.")
        return offsets

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Generates binary data and embeds flags at random offsets."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        output_path = challenge_folder / "hex_flag.bin"
        output_path.unlink(missing_ok=True)

        # 1. Setup Data
        binary_size = random.randint(1024, 1536)
        binary_data = bytearray(os.urandom(binary_size))
        
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        
        # Determine spans (flag + random padding)
        pads = [random.randint(1, 3) for _ in range(len(all_flags))]
        spans = [len(f) + p for f, p in zip(all_flags, pads)]
        offsets = self._get_offsets(binary_size, spans)

        # 2. Insert Flags
        for flag, offset, pad in zip(all_flags, offsets, pads):
            flag_bytes = flag.encode("utf-8") + (b" " * pad)
            binary_data[offset : offset + len(flag_bytes)] = flag_bytes

        output_path.write_bytes(binary_data)

        # 3. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(output_path.relative_to(self.project_root)),
            "unlock_method": "Inspect hex_flag.bin with a hex editor or strings command",
            "hint": "Try running 'strings hex_flag.bin' or open it in a hex editor like bless or GHex."
        }
        print(f"✅ Generated binary: {output_path.relative_to(self.project_root)}")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag