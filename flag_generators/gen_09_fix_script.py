#!/usr/bin/env python3

import sys
import random
import operator
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class FixScriptFlagGenerator:
    """
    Generator for the Fix the Script challenge.
    Creates a broken Python script that must be fixed to produce the flag.
    """

    OPERATORS = {
        "+": operator.add,
        "-": operator.sub,
        "*": operator.mul,
        "/": operator.floordiv # Using floor div to keep results integer-friendly
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

    def _get_valid_math(self):
        """Find parts where only one operator results in a 4-digit integer."""
        while True:
            target = random.randint(1000, 9999)
            op_sym = random.choice(list(self.OPERATORS.keys()))
            
            # Generate parts based on operator type
            if op_sym == "+":
                p1 = random.randint(100, target - 100)
                p2 = target - p1
            elif op_sym == "-":
                p1 = random.randint(target + 100, target + 1000)
                p2 = p1 - target
            elif op_sym == "*":
                # Find a divisor
                divisors = [i for i in range(2, 50) if target % i == 0]
                if not divisors: continue
                p2 = random.choice(divisors)
                p1 = target // p2
            elif op_sym == "/":
                p2 = random.randint(2, 25)
                p1 = target * p2

            # Verify exclusivity: check how many ops yield 4-digit results
            valid_ops = []
            for sym, func in self.OPERATORS.items():
                try:
                    res = func(p1, p2)
                    if 1000 <= res <= 9999:
                        valid_ops.append(sym)
                except ZeroDivisionError:
                    continue
            
            if len(valid_ops) == 1 and valid_ops[0] == op_sym:
                return op_sym, p1, p2, target

    def embed_flag(self, challenge_folder: Path, real_flag: str, suffix: int, correct_op: str, p1: int, p2: int):
        """Generates the broken python script."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        script_file = challenge_folder / "broken_flag.py"
        script_file.unlink(missing_ok=True)

        wrong_ops = [op for op in self.OPERATORS if op != correct_op]
        wrong_op = random.choice(wrong_ops)

        content = f"""#!/usr/bin/env python3

# This script should print: {real_flag}
# But the math operator is broken.

part1 = {p1}
part2 = {p2}

# MATH ERROR!
# Fix the operator to get the correct flag.
result = part1 {wrong_op} part2 

print(f"Your flag is: CCRI-SCRP-{{int(result)}}")
"""
        script_file.write_text(content)
        script_file.chmod(0o755)

        # Save Metadata
        self.metadata = {
            "real_flag": real_flag,
            "correct_operator": correct_op,
            "challenge_file": str(script_file.relative_to(self.project_root)),
            "unlock_method": "Fix the Python script’s math operator to calculate the flag",
            "hint": f"Find the broken operator in broken_flag.py and replace it with '{correct_op}'."
        }
        print(f"✅ Created: {script_file.relative_to(self.project_root)}")

    def generate_flag(self, challenge_folder: Path) -> str:
        correct_op, p1, p2, suffix = self._get_valid_math()
        real_flag = f"CCRI-SCRP-{suffix}"
        
        self.embed_flag(challenge_folder, real_flag, suffix, correct_op, p1, p2)
        return real_flag