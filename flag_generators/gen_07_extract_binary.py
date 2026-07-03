#!/usr/bin/env python3

import sys
import shutil
import subprocess
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class ExtractBinaryFlagGenerator:
    """
    Generator for the Extract Binary challenge.
    Compiles a C binary embedding flags using gcc.
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
        if not shutil.which("gcc"):
            raise RuntimeError("The 'gcc' compiler is not installed. Run 'apt install build-essential'.")

    def _run_cmd(self, cmd: list, cwd: Path, description: str):
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to {description}:\n{result.stderr.strip()}")

    def _generate_c_source(self, real_flag: str, fake_flags: list) -> str:
        """Generate the C source code with flag embedding."""
        junk_strings = [
            "ABCD1234XYZ!@#%$^&*()_+=?><~",
            "longgarbage....data...not...readable....random",
            "G@rb@g3StuffDataThatLooksBinaryButIsn't....",
            "%%%%%%%//////??????^^^^^*****&&&&&"
        ]
        
        if self.mode == "solo":
            junk_strings = [s[::-1] + "_solo" for s in junk_strings]

        binary_junk = ", ".join(str(random.randint(0, 255)) for _ in range(600))

        return f"""
#include <stdio.h>
#include <string.h>

__attribute__((used)) char flag1[] = "{fake_flags[0]}";
char junk1[300] = "{junk_strings[0]}";

__attribute__((used)) char flag2[] = "{real_flag}";
char junk2[500] = "{junk_strings[1]}";

__attribute__((used)) char flag3[] = "{fake_flags[1]}";
char junk3[400] = "{junk_strings[2]}";

__attribute__((used)) char flag4[] = "{fake_flags[2]}";
char junk4[600] = {{{binary_junk}}};

__attribute__((used)) char flag5[] = "{fake_flags[3]}";
char junk5[350] = "{junk_strings[3]}";

void keep_strings_alive() {{
    volatile char dummy = 0;
    dummy += flag1[0] + flag2[0] + flag3[0] + flag4[0] + flag5[0];
    dummy += junk1[0] + junk2[0] + junk3[0] + junk4[0] + junk5[0];
}}

int main() {{
    keep_strings_alive();
    return 0;
}}
"""

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Compile the binary and finalize metadata."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        c_file = challenge_folder / "hidden_flag.c"
        binary_file = challenge_folder / "hidden_flag"

        # 1. Write Source
        c_file.write_text(self._generate_c_source(real_flag, fake_flags))
        
        # 2. Compile
        try:
            self._run_cmd(
                ["gcc", "-O2", str(c_file), "-o", str(binary_file)],
                cwd=challenge_folder,
                description="compile C source with gcc"
            )
            print(f"🔨 Compiled binary: {binary_file.name}")
        finally:
            c_file.unlink(missing_ok=True)

        # 3. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(binary_file.relative_to(self.project_root)),
            "unlock_method": "Analyze binary with strings or disassembler to find flags",
            "hint": "Try using 'strings hidden_flag' or load it in radare2."
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = list({FlagUtils.generate_fake_flag() for _ in range(4)})
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag