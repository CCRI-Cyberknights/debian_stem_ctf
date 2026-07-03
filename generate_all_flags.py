#!/usr/bin/env python3

import argparse
import sys
import shutil
import json
from pathlib import Path

# === Import backend classes ===
# Assuming web_version_admin exists; keeping your imports for continuity
try:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "web_version_admin"))
    from ChallengeList import ChallengeList
except ImportError:
    print("⚠️ Note: ChallengeList not found. Proceeding with generator registry.")

# === Import all generators ===
from flag_generators.gen_01_stego import StegoFlagGenerator
from flag_generators.gen_02_base64 import Base64FlagGenerator
from flag_generators.gen_03_rot13 import ROT13FlagGenerator
from flag_generators.gen_04_vigenere import VigenereFlagGenerator
from flag_generators.gen_05_archive_password import ArchivePasswordFlagGenerator
from flag_generators.gen_06_hashcat import HashcatFlagGenerator
from flag_generators.gen_07_extract_binary import ExtractBinaryFlagGenerator
from flag_generators.gen_08_fake_auth_log import FakeAuthLogFlagGenerator
from flag_generators.gen_09_fix_script import FixScriptFlagGenerator
from flag_generators.gen_10_metadata import MetadataFlagGenerator
from flag_generators.gen_11_hidden_flag import HiddenFlagGenerator
from flag_generators.gen_12_qr_codes import QRCodeFlagGenerator
from flag_generators.gen_13_http_headers import HTTPHeaderFlagGenerator
from flag_generators.gen_14_internal_portals import InternalPortalFlagGenerator
from flag_generators.gen_15_process_inspection import ProcessInspectionFlagGenerator
from flag_generators.gen_16_hex_hunting import HexHuntingFlagGenerator
from flag_generators.gen_17_nmap_scanning import NmapScanFlagGenerator
from flag_generators.gen_18_pcap_search import PcapSearchFlagGenerator

GENERATOR_CLASSES = {
    "01_Stego": StegoFlagGenerator,
    "02_Base64": Base64FlagGenerator,
    "03_ROT13": ROT13FlagGenerator,
    "04_Vigenere": VigenereFlagGenerator,
    "05_ArchivePassword": ArchivePasswordFlagGenerator,
    "06_Hashcat": HashcatFlagGenerator,
    "07_ExtractBinary": ExtractBinaryFlagGenerator,
    "08_FakeAuthLog": FakeAuthLogFlagGenerator,
    "09_FixScript": FixScriptFlagGenerator,
    "10_Metadata": MetadataFlagGenerator,
    "11_HiddenFlag": HiddenFlagGenerator,
    "12_QRCodes": QRCodeFlagGenerator,
    "13_HTTPHeaders": HTTPHeaderFlagGenerator,
    "14_InternalPortals": InternalPortalFlagGenerator,
    "15_ProcessInspection": ProcessInspectionFlagGenerator,
    "16_HexHunting": HexHuntingFlagGenerator,
    "17_NmapScanning": NmapScanFlagGenerator,
    "18_PcapSearch": PcapSearchFlagGenerator,
}

# --- Helpers ---
def save_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

class FlagGenerationManager:
    def __init__(self, dry_run=False, mode="guided"):
        self.project_root = self._find_project_root()
        self.mode = mode
        self.dry_run = dry_run
        
        # Files
        self.challenges_dir = self.project_root / ("challenges" if mode == "guided" else "challenges_solo")
        self.unlocks_file = self.project_root / "web_version_admin" / (f"validation_unlocks{'_solo' if mode == 'solo' else ''}.json")
        
        self.validation_unlocks = {}
        if self.unlocks_file.exists():
            with open(self.unlocks_file, "r") as f:
                self.validation_unlocks = json.load(f)

    @staticmethod
    def _find_project_root():
        curr = Path.cwd()
        for parent in [curr] + list(curr.parents):
            if (parent / ".ccri_ctf_root").exists():
                return parent.resolve()
        raise FileNotFoundError("Could not find .ccri_ctf_root marker.")

    def generate_all(self):
        print(f"\n🌐 Starting Generation ({self.mode.upper()})...")
        success_count = 0
        
        for challenge_id, gen_cls in GENERATOR_CLASSES.items():
            print(f"🚀 Processing {challenge_id}...")
            try:
                # Setup folder
                target_folder = self.challenges_dir / challenge_id
                
                # Run generator
                gen = gen_cls(project_root=self.project_root, mode=self.mode)
                real_flag = gen.generate_flag(target_folder)
                
                # Update Metadata
                self.validation_unlocks[challenge_id] = gen.metadata
                success_count += 1
                print(f"✅ Finished {challenge_id}")
                
            except Exception as e:
                print(f"❌ Failed {challenge_id}: {e}")

        if not self.dry_run:
            save_json(self.unlocks_file, self.validation_unlocks)
            print(f"\n🎉 Saved {success_count} challenges to {self.unlocks_file.name}")

# --- Entry Point ---
if __name__ == "__main__":
    print("🌐 Select Mode: 1) Guided, 2) Solo, 3) Both")
    choice = input("Choice: ").strip()
    
    modes = []
    if choice == "1": modes = ["guided"]
    elif choice == "2": modes = ["solo"]
    elif choice == "3": modes = ["guided", "solo"]
    else: sys.exit(1)

    for m in modes:
        FlagGenerationManager(mode=m).generate_all()