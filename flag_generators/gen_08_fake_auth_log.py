#!/usr/bin/env python3

import sys
import random
import datetime
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class FakeAuthLogFlagGenerator:
    """
    Generator for the Fake Auth Log challenge.
    Creates a simulated auth.log with flags embedded as PIDs.
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

    def _generate_log_content(self, all_flags: list) -> str:
        """Constructs the full log content with embedded flags."""
        usernames = ["alice", "bob", "charlie", "dave", "eve"]
        ips = ["192.168.1.10", "192.168.1.20", "10.0.0.5", "172.16.0.3", "203.0.113.42", "127.0.0.1"]
        methods = ["password", "publickey"]
        
        line_count = 400 if self.mode == "solo" else 250
        fail_ratio = 0.6 if self.mode == "solo" else 0.2
        
        # Pick indices for flags
        flag_indices = sorted(random.sample(range(50, line_count - 20), len(all_flags)))
        flag_map = {idx: flag for idx, flag in zip(flag_indices, all_flags)}
        
        lines = []
        base_time = datetime.datetime.now()
        
        for i in range(line_count):
            timestamp = (base_time - datetime.timedelta(seconds=random.randint(0, 7200))).strftime("%b %d %H:%M:%S")
            user = random.choice(usernames)
            ip = random.choice(ips)
            method = random.choice(methods)
            result = "Accepted" if random.random() > fail_ratio else "Failed"
            
            # Use flag as PID if at target index, else random integer
            pid = flag_map.get(i, str(random.randint(1000, 99999)))
            
            lines.append(f"{timestamp} myhost sshd[{pid}]: {result} {method} for {user} from {ip} port {random.randint(1000, 65000)} ssh2")
            
        return "\n".join(lines)

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Creates the log file and saves metadata."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        log_path = challenge_folder / "auth.log"
        
        # Cleanup
        log_path.unlink(missing_ok=True)
        
        # Prepare Data
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        
        # Write Log
        log_path.write_text(self._generate_log_content(all_flags))
        print(f"📝 Created log: {log_path.relative_to(self.project_root)}")

        # Save Metadata
        self.metadata = {
            "real_flag": real_flag,
            "reconstructed_flag": real_flag,
            "challenge_file": str(log_path.relative_to(self.project_root)),
            "unlock_method": "Inspect auth.log for embedded flag in sshd PIDs",
            "hint": "Look for unusual process IDs in auth.log to spot the flag."
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        # Ensure uniqueness
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag