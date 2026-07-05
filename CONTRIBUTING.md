# 🤝 Contributing to `CCRI STEMDAY CTF` (Admin-Only)

Welcome to the **CCRI CyberKnights STEM Day CTF Project!** 🎉
This repository contains **all admin tools, source challenges, and packaging scripts** used to create the student VM and the public takehome version.

> ⚠️ **Important:** Students receive a **bundled version** where the answers are locked inside `ccri_ctf.pyz`.
> Never commit generated artifacts (`.pyz`, JSONs, builds) to this repo.

---

## 🗂️ Repo vs Bundles

We build three different versions from this single source of truth. All baseline build scripts utilize user-agnostic path discovery (relying on script-relative mapping or the `$SUDO_USER` calling variable) to make sure automation runs identically across development setups and clean VM deployments.

### 1. Admin Repo (This Source)
*The development environment containing all tools and secrets.*
```text
debian_stem_ctf/
├── challenges/              # Exploration (.explore.py + .coach.py)
├── challenges_solo/         # Solo challenges (README only)
├── web_version/             # Student-facing portal
├── web_version_admin/       # Admin-only validation + templates + student version generator
├── flag_generators/         # Scripts to create dynamic flags
├── validation_helpers/      # Helper scripts for the validator
├── copy_ccri_ctf*.py        # Bundling scripts (Normal, Solo, Takehome)
├── verify_workspace.py      # Master workspace validator & aggregator
├── generate_all_flags.py    # Flag + metadata generator
├── validate_all_flags.py    # Admin validator
├── setup_contributor.py     # Admin environment setup
├── reset_environment.py     # 🧹 Cleanup script
├── coach_core.py            # Engine Source (Includes Up-Arrow history and context tab-complete)
├── exploration_core.py      # Engine Source
├── worker_node.py           # Engine Source
└── README.md / CONTRIBUTING.md
```

### 2. Takehome / Public Repo
*Built via `copy_takehome_ccri_ctf.py` for public GitHub release.*
```text
ctf_takehome/
├── challenges/
├── challenges_solo/
├── web_version/
├── coach_core.py            # Engine Source
├── exploration_core.py      # Engine Source
├── worker_node.py           # Engine Source
├── setup_home_version.py    # User dependency installer
├── reset_environment.py     # User cleanup tool
├── VMSETUP.md               # Home user guide
└── ccri_ctf.pyz             # Bundled validation logic
```

### 3. Student VM / Cyber Range Template (Event Day)
*Deployed via `copy_ccri_ctf.py` to the Student User desktop.*
```text
/home/stemctf/Desktop/ccri_ctf/
├── challenges/              # Guided mode
├── challenges_solo/         # Hard mode
├── web_version/
├── coach_core.py            # Engine Source
├── exploration_core.py      # Engine Source
├── worker_node.py           # Engine Source
├── start_web_hub.py
├── stop_web_hub.py
└── ccri_ctf.pyz             # Bundled validation logic
```
*Note: The master system deployment template injects persistent tmux modifications directly into user skeleton setups (/etc/skel/.tmux.conf) to force mouse tracking and click-to-focus navigation features by default.*

---

## 🚀 Contributor Setup

1.  **Bootstrap the Contributor Environment:**
    Run the unified curl installer stream. This script automatically handles package provisioning, system grouping updates, and configures the development directory parameters:
    ```bash
    sudo apt update && sudo apt install curl -y && curl -fsSL https://raw.githubusercontent.com/CCRI-Cyberknights/debian_stem_ctf/refs/heads/main/setup_contributor.py | python3 -
    ```

2.  **Enter the Workspace Directory:**
    ```bash
    cd debian_stem_ctf
    ```

3.  **Create a branch for your work:**
    ```bash
    git checkout -b feature/my-change
    ```

---

## 🛠 Workflow

When working on core assets, challenge tracks, or updating systemic mechanics, contributors must advance through the pipeline sequence in this exact order:

1.  **Verify Workspace and Generate Initial Assets:**
    Instead of calling standalone creation variables independently, execute the master pipeline controller. This script checks environment paths, spins up the asset build generator (`generate_all_flags.py`), tracks system states, and sequentially handles execution validation across all 18 challenge modules:
    ```bash
    ./verify_workspace.py
    ```

2.  **Compile the Web Architecture Layout:**
    Once your baseline workspace verification script returns clean, initialize the administrative build engine to compile the front-facing student web platform deployment assets:
    ```bash
    ./web_version_admin/build_web_version
    ```

3.  **Deploy Local Installation Snapshots for Validation:**
    Test local behavioral states by launching your preferred targeted copy wrapper:
    ```bash
    ./copy_ccri_ctf.py
    ```
    *   **Exploration mode verification:** Verify that your changes interact accurately with the "Cyber Coach" panel. Test that input hooks log to the readline up-arrow history pool and that the context-aware autocomplete engine successfully discovers cross-directory challenge targets.
    *   **Sandbox Container sanity checks:** If configuring external range components (such as the OWASP Juice Shop platform on port 3000 or the isolated Command Line Murder Mystery shell container layer), execute your desktop shortcut configurations to guarantee that transient container state wipes occur properly upon task exit.

4.  **Wipe Runtime State Garbage Before Committing:**
    Before executing a staging commit, purge temporary binaries and state tracking logs to prevent corrupted tracking updates:
    ```bash
    ./reset_environment.py
    ```

5.  **Commit cleanly:**
    ```bash
    git add .
    git commit -m "Add: new ROT13 challenge configuration"
    git push origin feature/my-change
    ```

---

## 📝 Markdown & Testing

I've included a markdown cheatsheet here: [Markdown Cheatsheet](./markdown-cheat-sheet.md).

* See it on the GitHub webpage for examples.
* **To test README edits:** Start the webserver in admin mode (`./start_web_hub.py`), load the page with the specific readme, and see how it renders.

---

## 🛡️ Rules & Best Practices

✅ **Standard Naming:**
* Helper scripts: **`.explore.py`**
* Coach scripts: **`.coach.py`**

✅ **.pyz is the only runtime path for answers:** This structure locks validation logic safe from local user space visibility or accidental leakage points.

✅ **Never commit:**
* `ccri_ctf.pyz`
* `validation_unlocks*.json`
* Generated challenge artifacts (binaries, pcap files, logs, etc.)
* Take-home bundles or packaged folders
* Active Python `.venv` structural configurations

✅ **Use `reset_environment.py`** to ensure your branch doesn't include generated garbage.

✅ **PRs should explain:**
* Which challenges/scripts changed.
* Whether flags were regenerated.

---

## 🙌 Thanks for Contributing!

Every improvement helps make CCRI STEM Day a smoother, more resilient experience for students. 🚩