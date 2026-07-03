#!/usr/bin/env python3

import sys
import json
import base64
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class InternalPortalFlagGenerator:
    """
    Generator for the Internal Portals challenge.
    Encodes HTML portal pages into a Base64-encoded .server_data blob.
    """

    PORTAL_CONFIGS = {
        "guided": [
            ("alpha", "Alpha Service", "All systems operational."),
            ("beta", "Beta Dashboard", "Restricted Access."),
            ("gamma", "Gamma API", "Maintenance Mode."),
            ("delta", "Delta Service", "API Online."),
            ("omega", "Omega Tools", "Internal Testing.")
        ],
        "solo": [
            ("sector-1", "Restricted Zone 1", "Auth required."),
            ("sector-2", "Restricted Zone 2", "Camera feed active."),
            ("sector-3", "Restricted Zone 3", "Data retention policy."),
            ("sector-4", "Restricted Zone 4", "Maintenance access only."),
            ("sector-5", "Restricted Zone 5", "Offline.")
        ]
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

    def _get_html_template(self, title: str, desc: str, flag: str, domain: str) -> str:
        """Generates the HTML structure with embedded flag."""
        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset='UTF-8'>
  <title>{title}</title>
  <style>body {{ font-family: monospace; padding: 2rem; }}</style>
</head>
<body>
  <h1>{title}</h1>
  <p>{desc}</p>
  <hr>
  <span style='display:none' id='debug-info'>Flag: {flag}</span>
  <p>System ID: {domain}</p>
</body>
</html>"""

    def embed_data(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Constructs the .server_data blob."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        target_file = challenge_folder / ".server_data"
        target_file.unlink(missing_ok=True)

        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        server_data = {}
        portals = self.PORTAL_CONFIGS[self.mode]

        for (name, title, desc), flag in zip(portals, all_flags):
            server_data[name] = self._get_html_template(title, desc, flag, name)
            if flag == real_flag:
                print(f"✅ Flag hidden in: {name}")

        # Encode and Write
        json_str = json.dumps(server_data)
        b64_data = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        target_file.write_text(b64_data, encoding='utf-8')

        # Metadata
        url_hint = "sector-X" if self.mode == "solo" else "alpha/beta/..."
        self.metadata = {
            "real_flag": real_flag,
            "challenge_folder": str(challenge_folder.relative_to(self.project_root)),
            "unlock_method": "Inspect DOM / View Source",
            "hint": f"Check hidden span elements on {url_hint}"
        }
        print(f"📄 Created: {target_file.relative_to(self.project_root)}")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        return real_flag