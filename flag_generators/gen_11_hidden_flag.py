#!/usr/bin/env python3

import sys
import shutil
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class HiddenFlagGenerator:
    """
    Generator for the Hidden Flag challenge.
    Builds a fake folder structure and hides flags in random files.
    """

    FOLDERS_AND_FILES = {
        "backup": ["sysdump.bak", ".config.old"],
        "data": ["info.tmp", ".hint_file", ".summary"],
        "logs": ["old.log", ".keep.tmp", ".notes"],
        "ref": ["readme.txt", ".archive"],
    }

    FILE_JUNK = {
        "sysdump.bak": ["### System Memory Dump ###", "Heap analysis: no anomalies detected.", "Saved core dump."],
        ".config.old": ["# Legacy config", "user=guest", "enable_logging=true"],
        "info.tmp": ["[INFO BLOCK]", "Session start: 2025-06-21", "User: ccri_admin"],
        ".hint_file": ["# HINT: Metadata matters.", "Cross-check all files."],
        ".summary": ["=== Data Summary Report ===", "Total records: 1024"],
        "old.log": ["[2025-06-19] INFO User login attempt.", "[2025-06-19] WARN Disk usage 92%."],
        ".keep.tmp": ["# Temporary File", "Checksum: a9b8c7d6e5f4"],
        ".notes": ["Research notes.", "TODO: Encryption key rotation."],
        "readme.txt": ["Welcome.", "Review each file carefully."],
        ".archive": ["# Archive header", "Created by archiver v2.1"],
    }

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

    def _generate_junk_content(self, file_name: str, flag: str = None) -> str:
        """Returns randomized file content with or without a flag."""
        snippets = self.FILE_JUNK.get(file_name, ["# Generic placeholder content"])
        lines = random.choices(snippets, k=random.randint(3, 7))
        if flag:
            insert_pos = random.randint(0, len(lines))
            lines.insert(insert_pos, flag)
        return "\n".join(lines)

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Creates the folder structure and hides flags in files."""
        # 1. Cleanup
        if challenge_folder.exists():
            shutil.rmtree(challenge_folder)
        challenge_folder.mkdir(parents=True, exist_ok=True)

        # 2. Map files to locations
        all_files = []
        for folder, files in self.FOLDERS_AND_FILES.items():
            folder_path = challenge_folder / folder
            folder_path.mkdir(exist_ok=True)
            for f in files:
                all_files.append(folder_path / f)

        # 3. Assign flags to files
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        
        # Select 5 files to hold flags
        target_files = random.sample(all_files, len(all_flags))
        flag_map = {path: flag for path, flag in zip(target_files, all_flags)}

        # 4. Write files
        for file_path in all_files:
            flag = flag_map.get(file_path)
            content = self._generate_junk_content(file_path.name, flag)
            file_path.write_text(content)

        print(f"📁 Created hidden file structure in: {challenge_folder.relative_to(self.project_root)}")

        # 5. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_folder": str(challenge_folder.relative_to(self.project_root)),
            "unlock_method": "Search recursively for the flag in hidden files",
            "hint": "Use grep -R or find/strings to locate the flag in junk/"
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder / "junk", real_flag, fake_flags)
        return real_flag