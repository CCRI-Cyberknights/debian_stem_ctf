#!/usr/bin/env python3

import json
import base64
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class HTTPHeaderFlagGenerator:
    """
    Generator for the HTTP Headers challenge.
    Produces a hidden .server_data file containing encoded endpoint configurations.
    """

    SERVERS = ["CryptKeepers-Gateway/2.3.1", "CryptKeepers-Node/3.0.0-beta", "Apache/2.4.54", "nginx/1.24.0", "Go HTTP Server/1.19"]
    POWERED_BY = ["PHP/8.1.12", "Python/3.11.4", "Node.js/18.16.0", "ASP.NET Core/7.0", "Ruby on Rails/7.1.0"]
    CONTENT_TYPES = ["text/html; charset=UTF-8", "application/json", "text/plain; charset=UTF-8"]
    CACHE_CONTROLS = ["no-store", "public, max-age=86400", "private, no-cache"]
    HTML_BODIES = [
        "<html><head><title>Portal</title></head><body><h1>CryptKeepers Hub</h1><p>System maintenance active.</p></body></html>",
        "<html><head><title>Dashboard</title></head><body><h1>Ops Dashboard</h1><p>Redirecting...</p></body></html>",
        "<html><head><title>Data</title></head><body><h1>Data Service</h1><p>Ready.</p></body></html>",
        '{"status": "ok", "message": "API v1.2.4", "notes": "Nominal"}',
        "CryptKeepers plain text endpoint. Status: OK"
    ]

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

    def _generate_endpoint(self, flag: str) -> dict:
        """Creates the headers and body for a single endpoint."""
        headers = {
            "Server": random.choice(self.SERVERS),
            "Content-Type": random.choice(self.CONTENT_TYPES),
            "Cache-Control": random.choice(self.CACHE_CONTROLS),
            "X-Powered-By": random.choice(self.POWERED_BY),
            "X-Frame-Options": "SAMEORIGIN",
            "X-Content-Type-Options": "nosniff",
            "X-Flag": flag
        }

        if random.random() < 0.6:
            session_id = ''.join(random.choices("abcdef0123456789", k=16))
            headers["Set-Cookie"] = f"sessionid={session_id}; HttpOnly; Secure"

        return {
            "headers": headers,
            "body": random.choice(self.HTML_BODIES),
            "status_code": 200
        }

    def embed_data(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Creates the .server_data blob."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        target_file = challenge_folder / ".server_data"
        target_file.unlink(missing_ok=True)

        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        server_data = {}
        key_prefix = "channel" if self.mode == "solo" else "endpoint"

        for i, flag in enumerate(all_flags, start=1):
            server_data[f"{key_prefix}_{i}"] = self._generate_endpoint(flag)

        # Encode and Write
        json_str = json.dumps(server_data)
        b64_data = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
        target_file.write_text(b64_data)

        # Metadata
        url_ex = "/covert/channel_X" if self.mode == "solo" else "/mystery/endpoint_X"
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(target_file.relative_to(self.project_root)),
            "unlock_method": f"Use curl -I to check headers of {url_ex}",
            "hint": "Check X-Flag header"
        }
        print(f"📄 Created: {target_file.relative_to(self.project_root)}")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        print(f"✅ {self.mode.capitalize()} flag: {real_flag}")
        return real_flag