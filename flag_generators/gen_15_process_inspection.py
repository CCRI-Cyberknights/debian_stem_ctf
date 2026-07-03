#!/usr/bin/env python3

import random
from pathlib import Path
from flag_generators.flag_helpers import FlagUtils

class ProcessInspectionFlagGenerator:
    """
    Generator for the Process Inspection challenge.
    Produces ps_dump.txt with real and fake flags in process listings.
    """

    USERS = ["root", "user1", "user2", "user3", "daemon", "syslog", "mysql", "postfix", "nobody", "ckeepers"]
    COMMANDS = [
        "/usr/sbin/apache2 -k start",
        "/usr/bin/nano /home/user{}/notes.txt",
        "/usr/bin/python3 /usr/lib/update-manager/check-new-release",
        "/usr/bin/firefox --no-remote",
        "/usr/bin/gedit /home/user{}/todo.txt",
        "/usr/bin/vlc /home/user{}/video.mp4",
        "/usr/sbin/ufw --daemon",
        "/usr/sbin/rsyslogd -n",
        "/usr/bin/thunderbird",
        "/usr/sbin/sshd -D",
        "/usr/sbin/acpid",
        "/usr/bin/htop",
        "/usr/bin/code /home/user{}/project",
        "/lib/systemd/systemd-journald",
        "/usr/sbin/cron -f",
        "/usr/sbin/irqbalance",
        "/usr/local/bin/tunneler --mode passive --ttl 128",
        "/usr/bin/harvest --scan --output /tmp/result.log",
        "/opt/cryptkeepers/bin/siphon --threads 8 --proxy 127.0.0.1:8080"
    ]

    FLAG_PROCESSES = [
        "/usr/bin/harvest --target 10.6.42.18 --flag={} --interval 15 --verbose",
        "/opt/cryptkeepers/bin/siphon --upload --flag={} --threads 4",
        "/usr/local/bin/tunneler --flag={} --mode aggressive --ttl 64",
        "/usr/bin/stealth --flag={} --timeout 90",
        "/usr/sbin/backdoor --flag={} --listen --port 4444"
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

    def _generate_proc_line(self, user=None, cmd=None) -> str:
        """Generates a single line mimicking 'ps aux' output."""
        user = user or random.choice(self.USERS)
        cmd = cmd or random.choice(self.COMMANDS).format(random.randint(1, 3))
        
        pid = random.randint(100, 9999)
        cpu = round(random.uniform(0.1, 1.5), 1)
        mem = round(random.uniform(0.1, 1.5), 1)
        vsz = random.randint(15000, 80000)
        rss = random.randint(3000, 40000)
        tty = random.choice(["?", "pts/0", "pts/1"])
        stat = random.choice(["S", "Ss", "Sl", "Ssl", "R", "R+", "Z", "D"])
        start = f"Jul{random.randint(1, 30):02d}"
        time = f"{random.randint(0, 2)}:{random.randint(0, 59):02d}"

        return f"{user:<10}{pid:<6}{cpu:<5}{mem:<5}{vsz:<8}{rss:<7}{tty:<10}{stat:<5}{start:<8}{time:<7}{cmd}"

    def embed_flags(self, challenge_folder: Path, real_flag: str, fake_flags: list):
        """Constructs the ps_dump.txt file with embedded flags."""
        challenge_folder.mkdir(parents=True, exist_ok=True)
        dump_file = challenge_folder / "ps_dump.txt"
        dump_file.unlink(missing_ok=True)

        lines = ["USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND"]
        
        # 1. Generate Noise
        for _ in range(random.randint(80, 100)):
            lines.append(self._generate_proc_line())

        # 2. Add Flag Processes
        all_flags = fake_flags + [real_flag]
        random.shuffle(all_flags)
        random.shuffle(self.FLAG_PROCESSES)

        for proc_tmpl, flag in zip(self.FLAG_PROCESSES, all_flags):
            lines.append(self._generate_proc_line(user="ckeepers", cmd=proc_tmpl.format(flag)))

        # 3. Finalize
        random.shuffle(lines[1:]) # Preserve header
        dump_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        self.metadata = {
            "real_flag": real_flag,
            "challenge_file": str(dump_file.relative_to(self.project_root)),
            "unlock_method": "Inspect ps_dump.txt for flags embedded in process commands",
            "hint": "Use grep to search for flags in ps_dump.txt"
        }
        print(f"📝 Created {dump_file.relative_to(self.project_root)}")

    def generate_flag(self, challenge_folder: Path) -> str:
        real_flag = FlagUtils.generate_real_flag()
        fake_flags = [FlagUtils.generate_fake_flag() for _ in range(4)]
        
        while real_flag in fake_flags:
            real_flag = FlagUtils.generate_real_flag()

        self.embed_flags(challenge_folder, real_flag, fake_flags)
        print(f"✅ {self.mode.capitalize()} flag: {real_flag}")
        return real_flag