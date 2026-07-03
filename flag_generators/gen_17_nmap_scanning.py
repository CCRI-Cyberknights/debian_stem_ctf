#!/usr/bin/env python3

import sys
import json
import random
import re
import shutil
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class NmapScanFlagGenerator:
    """
    Generator for the Nmap Scanning challenge.
    Dynamically patches fake_services.py with random port configurations.
    """

    SERVICE_NAME_POOL = [
        "alpha-core", "delta-sync", "gamma-relay", "beta-hub", "lambda-api", "omega-stream",
        "theta-daemon", "epsilon-sync", "kappa-node", "zeta-cache", "delta-proxy",
        "sysmon-api", "configd", "metricsd", "auth-service", "update-agent"
    ]

    JUNK_RESPONSES = [
        "Welcome to Dev HTTP Server v1.3\nPlease login to continue.",
        "🔒 Unauthorized: API key required.",
        "503 Service Unavailable\nTry again later.",
        "<html><body><h1>It works!</h1><p>Apache2 default page.</p></body></html>",
        "DEBUG: Connection established successfully.",
        "💡 Tip: Scan only the ports you really need.",
        "ERROR 400: Bad request syntax.",
        "System maintenance in progress.",
        "Welcome to Experimental IoT Server (beta build).",
        "Python HTTP Server: directory listing not allowed.",
        "💻 Dev API v0.1 — POST requests only.",
        "403 Forbidden: You don’t have permission to access this resource.",
        "Error 418: I’m a teapot.",
        "Hello World!\nTest endpoint active.",
        "Server under maintenance.\nPlease retry later."
    ]

    def __init__(self, project_root: Path = None, mode="guided"):
        self.project_root = project_root or self._find_project_root()
        self.mode = mode.lower()
        self.services_file = self.project_root / "web_version_admin" / "fake_services.py"
        self.port_range = list(range(8000, 8100)) if self.mode == "guided" else list(range(9000, 9100))
        self.metadata = {}

    @staticmethod
    def _find_project_root() -> Path:
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find .ccri_ctf_root marker.")

    def _escape_python_string(self, s: str) -> str:
        return '"' + s.replace('\\', '\\\\').replace('\n', '\\n').replace('"', '\\"') + '"'

    def _patch_services_file(self, real_flag: str, fake_flags: dict, real_port: int, junk_ports: dict):
        """Updates the fake_services.py file using regex pattern matching."""
        if not self.services_file.exists():
            raise FileNotFoundError(f"Service file not found: {self.services_file}")

        # Data blocks
        flag_var = "GUIDED_FAKE_FLAGS" if self.mode == "guided" else "SOLO_FAKE_FLAGS"
        junk_var = "GUIDED_JUNK_RESPONSES" if self.mode == "guided" else "SOLO_JUNK_RESPONSES"
        service_var = "GUIDED_SERVICE_NAMES" if self.mode == "guided" else "SOLO_SERVICE_NAMES"

        all_ports = [real_port] + list(fake_flags.keys()) + list(junk_ports.keys())
        random.shuffle(self.SERVICE_NAME_POOL)
        service_names = {port: self.SERVICE_NAME_POOL[i % len(self.SERVICE_NAME_POOL)] for i, port in enumerate(all_ports)}

        # Construct code blocks
        new_fake_flags_block = f"{flag_var} = {{\n    {real_port}: \"{real_flag}\",  # ✅ REAL FLAG\n" + \
                               "\n".join([f"    {p}: \"{f}\"," for p, f in fake_flags.items()]) + "\n}"

        new_junk_block = f"{junk_var} = {{\n" + \
                         ",\n".join([f"    {p}: {self._escape_python_string(junk_ports[p])}" for p in sorted(junk_ports)]) + "\n}"

        new_services_block = f"{service_var} = {{\n" + \
                             ",\n".join([f"    {p}: \"{service_names[p]}\"" for p in sorted(service_names)]) + "\n}"

        # Apply Patch
        content = self.services_file.read_text(encoding="utf-8")
        
        # Helper to replace blocks
        def patch_block(var_name, block_content, text):
            pattern = rf"{var_name}\s*=\s*\{{[^}}]*\}}"
            new_text, count = re.subn(pattern, block_content, text, flags=re.DOTALL)
            if count == 0:
                raise RuntimeError(f"Could not patch {var_name}")
            return new_text

        content = patch_block(flag_var, new_fake_flags_block, content)
        content = patch_block(junk_var, new_junk_block, content)
        
        # Backup and Save
        backup = self.services_file.with_suffix(".bak")
        if not backup.exists():
            shutil.copy(self.services_file, backup)
            
        self.services_file.write_text(content, encoding="utf-8")
        print(f"✅ Patched {self.services_file.name}")

    def generate_flag(self, challenge_folder: Path) -> str:
        # Setup Data
        available_ports = set(self.port_range)
        selected_ports = random.sample(sorted(available_ports), 15)
        
        real_port = selected_ports[0]
        real_flag = FlagUtils.generate_real_flag()
        
        # Fake Flags & Junk
        fake_ports = selected_ports[1:5]
        fake_flags = {p: FlagUtils.generate_fake_flag() for p in fake_ports}
        
        junk_ports = {p: random.choice(self.JUNK_RESPONSES) for p in selected_ports[5:]}

        # Apply to infrastructure
        self._patch_services_file(real_flag, fake_flags, real_port, junk_ports)

        # Update metadata
        self.metadata = {
            "real_flag": real_flag,
            "real_port": real_port,
            "server_file": str(self.services_file.relative_to(self.project_root)),
            "unlock_method": f"Scan ports {self.port_range[0]}–{self.port_range[-1]} to locate the flag (port {real_port})",
            "hint": f"Use nmap -p{self.port_range[0]}-{self.port_range[-1]} localhost to discover ports and curl to check flags."
        }

        return real_flag