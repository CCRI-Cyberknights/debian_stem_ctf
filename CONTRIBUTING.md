# 🤝 Contributing to `CCRI STEMDAY CTF` (Admin-Only)

Welcome to the **CCRI CyberKnights STEM Day CTF Project!** 🎉
This repository contains **all admin tools, source challenges, and packaging scripts** used to create the student VM and the public takehome version.

> ⚠️ **Important:** Students receive a **bundled version** where the answers are locked inside `ccri_ctf.pyz`.
> Never commit generated artifacts (`.pyz`, JSONs, builds) to this repo.

---

## 🗂️ Repo vs Bundles

We build three different versions from this single source of truth.

### 1. Admin Repo (This Source)
*The development environment containing all tools and secrets.*
```text
debian_stem_ctf/
├── challenges/              # Exploration (.explore.py + .coach.py)
├── challenges_solo/         # Solo challenges (README only)
├── web_version/             # Student-facing portal
├── web_version_admin/       # Admin-only validation + templates + student version generator
├── debs/                    # Debian packages for installation
├── flag_generators/         # Scripts to create dynamic flags
├── validation_helpers/      # Helper scripts for the validator
├── copy_ccri_ctf*.py        # Bundling scripts (Normal, Solo, Takehome)
├── generate_all_flags.py    # Flag + metadata generator
├── validate_all_flags.py    # Admin validator
├── setup_contributor.py     # Admin environment setup
├── reset_environment.py     # 🧹 Cleanup script
├── coach_core.py            # Engine Source
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

### 3. Student VM (Event Day)
*Deployed via `copy_ccri_ctf.py` to the Student User.*
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

---

## 🚀 Contributor Setup

1.  **Install contributor environment:**

    ```bash
    sudo apt update && sudo apt install curl -y
    curl -fsSL https://raw.githubusercontent.com/CCRI-Cyberknights/debian_stem_ctf/refs/heads/main/setup_contributor.py | python3 -
    ```

2.  **Clone repo:**

    ```bash
    git clone https://github.com/CCRI-Cyberknights/debian_stem_ctf.git
    cd debian_stem_ctf
    ```

3.  **Create a branch for your work:**

    ```bash
    git checkout -b feature/my-change
    ```

---

## 🛠 Workflow

1.  **Generate fresh flags** (only if working on challenges):

    ```bash
    ./generate_all_flags.py
    ```

2.  **Test locally**:

    * **Exploration mode**: run `./copy_ccri_ctf.py` and launch hub.
    * **Solo mode**: run `./copy_ccri_ctf_solo.py` and launch hub.
    * **Takehome Repo**: run `./copy_takehome_ccri_ctf.py` to inspect the output folder.
    * **Validate Logic**:
        ```bash
        ./validate_all_flags.py
        ```

3.  **Clean Up**:
    Before committing, remove all generated files to keep the PR clean:
    ```bash
    ./reset_environment.py
    ```

4.  **Commit cleanly**:

    ```bash
    git add .
    git commit -m "Add: new ROT13 challenge"
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

✅ **.pyz is the only runtime path for answers** — no source leaks for validation logic.

✅ **Never commit:**
* `ccri_ctf.pyz`
* `validation_unlocks*.json`
* Generated challenge artifacts (binaries, pcap files, logs, etc.)
* Take-home bundles or packaged folders

✅ **Use `reset_environment.py`** to ensure your branch doesn't include generated garbage.

✅ **PRs should explain:**
* Which challenges/scripts changed.
* Whether flags were regenerated.

---

## 🙌 Thanks for Contributing!

Every improvement helps make CCRI STEM Day a smoother experience for students. 🚩
