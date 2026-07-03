#!/usr/bin/env python3

import sys
import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

# Scapy is an optional dependency for the generator environment
try:
    from scapy.all import IP, TCP, Raw, wrpcap
except ImportError:
    print("❌ Scapy is not installed. Run: sudo apt install python3-scapy")
    sys.exit(1)

class PcapSearchFlagGenerator:
    """
    Generator for the PCAP Search challenge.
    Creates a traffic.pcap with embedded real and fake flags in HTTP headers.
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

    def _create_http_packet(self, src: str, dst: str, sport: int, dport: int, payload: bytes):
        """Helper to build a single HTTP packet."""
        return IP(src=src, dst=dst) / TCP(sport=sport, dport=dport, flags="PA", seq=random.randint(1000, 5000)) / Raw(load=payload)

    def _generate_conversation(self, src: str, dst: str, flag: str = None, noise: bool = False) -> list:
        """Generates a request/response pair."""
        sport = random.randint(1024, 65535)
        dport = 80
        packets = []

        # Request
        req_payload = f"GET / HTTP/1.1\r\nHost: {dst}\r\nUser-Agent: Mozilla/5.0\r\n\r\n".encode()
        packets.append(self._create_http_packet(src, dst, sport, dport, req_payload))

        # Response
        headers = [
            "HTTP/1.1 200 OK",
            "Server: nginx/1.18.0",
            "Content-Type: text/html",
            f"Set-Cookie: sessionid={''.join(random.choices('abcdef1234567890', k=10))}; HttpOnly"
        ]
        
        if flag:
            headers.append(f"X-Flag: {flag}")
            body = "<html><body><p>Authorized access.</p></body></html>"
        elif noise:
            body = "<html><body><p>Welcome to our web server.</p></body></html>"
        else:
            body = "<html><body><p>Hello, authorized user.</p></body></html>"

        resp_payload = f"{chr(13).join(headers)}\r\n\r\n{body}".encode()
        packets.append(self._create_http_packet(dst, src, dport, sport, resp_payload))
        
        return packets

    def embed_pcap(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Generates traffic.pcap containing the flags."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        output_file = challenge_folder / "traffic.pcap"
        output_file.unlink(missing_ok=True)

        packets = []

        # 1. Add Noise
        for _ in range(150):
            src = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            dst = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            packets.extend(self._generate_conversation(src, dst, noise=True))

        # 2. Add Flags
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)

        for flag in all_flags:
            # Random IPs for flag traffic
            src = f"172.16.{random.randint(0,255)}.{random.randint(1,254)}"
            dst = f"172.16.{random.randint(0,255)}.{random.randint(1,254)}"
            packets.extend(self._generate_conversation(src, dst, flag=flag))

        # 3. Write PCAP
        random.shuffle(packets)
        wrpcap(str(output_file), packets)
        print(f"✅ Generated: {output_file.relative_to(self.project_root)}")

        # 4. Metadata
        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(output_file.relative_to(self.project_root)),
            "unlock_method": "Analyze traffic.pcap for flags in HTTP headers using Wireshark or tshark",
            "hint": "Filter for HTTP headers (e.g., `http.header`) or grep for `X-Flag:`"
        }

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_pcap(challenge_folder, real_flag, fake_flags)
        print(f"✅ {self.mode.capitalize()} flag: {real_flag}")
        return real_flag