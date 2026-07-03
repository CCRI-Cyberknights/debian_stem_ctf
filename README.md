# 🌟 CCRI CyberKnights STEM Day Project
 
> This project was originally developed for Parrot OS (6.4). It has been ported to **Debian 13 (Trixie)** for continued use.

Welcome to the **CCRI CyberKnights STEM Day VM Project!** 🎉  
This repository powers the custom **Capture The Flag (CTF)** environment used for local STEM outreach.

👥 **This repository is for CCRI CyberKnights club members only.** It contains source files, administrative automation, and build scripts used to deploy the student-facing CTF environment.

---

## 🌀 Quick Setup (Admin/Dev Environment)

**Clone the repo and initialize your environment:**

```bash
git clone https://github.com/CCRI-Cyberknights/debian_stem_ctf.git
cd debian_stem_ctf
# Ensure you have standard Python build tools installed
sudo apt update && sudo apt install python3 python3-pip python3-venv
```

---

## 📜 Script Reference

### 📦 Build & Deployment
These scripts handle the packaging and environment population for various student use cases.

| Script | Function |
| :--- | :--- |
| **`copy_ccri_ctf.py`** | **Standard Build.** Populates the student VM with full content (Exploration + Solo modes). |
| **`copy_ccri_ctf_solo.py`** | **Solo-Only Build.** A stripped-down build containing only challenges_solo. Removes guided scripts/coaches. |
| **`copy_takehome_ccri_ctf.py`** | **Take-Home Build.** Exports student-facing assets to the ctf_takehome directory for distribution. |

### ⚙️ Core Engines
The backend logic powering the interactive CTF components.

| Script | Function |
| :--- | :--- |
| **`coach_core.py`** | **Coach Mode.** Handles hint logic and interaction with the "Cyber Coach." |
| **`exploration_core.py`** | **Exploration Mode.** Manages challenge state and guided tutorials. |
| **`worker_node.py`** | Helper for sub-process execution and secure flag validation. |

### 🚩 Flag Lifecycle & Admin
Tools for generating content and testing system integrity.

| Script | Function |
| :--- | :--- |
| **`generate_all_flags.py`** | Generates real/fake flags, challenge binaries, and challenges.json metadata. |
| **`validate_all_flags.py`** | **Master Validator.** Runs all 18 individual challenge validators to ensure total system integrity. |
| **`reset_environment.py`** | **Cleanup.** Purges generated binaries, flags, and temp files for a clean state. |

### 🌐 Web Interface
| Script | Function |
| :--- | :--- |
| **`start_web_hub.py`** | Launches the offline Flask web server (The Hub where students verify flags). |
| **`stop_web_hub.py`** | Gracefully shuts down the web hub. |

---

## 🚀 Workflow for Contributors

1.  **Generate Assets:**
    ```bash
    ./generate_all_flags.py
    ```
2.  **Test Environment:**
    *   Verify individual components: `./validate_all_flags.py`
    *   Check for errors in stderr.
3.  **Build Deployment:**
    *   To simulate a student installation: `./copy_ccri_ctf.py`
4.  **Clean Up (Pre-Commit):**
    *   **Always** run this before committing changes:
    ```bash
    ./reset_environment.py
    ```

---

## 🙌 Best Practices & Notes

* **Security:** Admin-only JSON files (validation_unlocks*.json) must **never** be committed to public branches.
* **Packaging:** .pyz files are the only runtime path for students; this bundles logic while preventing source code leaks.
* **Environment:** This project assumes a Debian-based environment. Ensure python3-venv is used for local development to avoid conflicting with system-level packages.

---

## 📖 Contributing

Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide for branching strategies, PR workflows, and best practices for adding new challenges.