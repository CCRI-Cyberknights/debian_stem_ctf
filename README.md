# 🌟 CCRI CyberKnights STEM Day Project

> This project was originally developed for Parrot OS (6.4). It has been ported to **Debian 13 (Trixie)** for continued use.

Welcome to the **CCRI CyberKnights STEM Day VM Project!** 🎉  
This repository powers the custom **Capture The Flag (CTF)** environment used for local STEM outreach.

👥 **This repository is for CCRI CyberKnights club members only.** It contains source files, administrative automation, and build scripts used to deploy the student-facing CTF environment.

---

## 🌀 Quick Setup (Admin/Dev Environment)

**Initialize your environment using the automated contributor setup script:**

```bash
sudo apt update && sudo apt install curl -y && curl -fsSL https://raw.githubusercontent.com/CCRI-Cyberknights/debian_stem_ctf/refs/heads/main/setup_contributor.py | python3 -
```

*Note: All core deployment and compilation scripts utilize user-agnostic path discovery. They dynamically resolve target locations relative to the script runtime context or via the $SUDO_USER invocation wrapper, meaning repository management functions cleanly under any valid environment account without hardcoded path dependencies.*

---

## 📜 Script Reference

### 📦 Build & Deployment
These scripts handle the packaging and environment population for various student use cases.

| Script | Function |
| :--- | :--- |
| **`copy_ccri_ctf.py`** | **Standard Build.** Populates the student VM with full content (Exploration + Solo modes). |
| **`copy_ccri_ctf_solo.py`** | **Solo-Only Build.** A stripped-down build containing only challenges_solo. Removes guided scripts and coaches. |
| **`copy_takehome_ccri_ctf.py`** | **Take-Home Build.** Exports student-facing assets to the ctf_takehome directory for distribution. Safely isolates local .venv dependencies dynamically. |

### ⚙️ Core Engines
The backend logic powering the interactive CTF components.

| Script | Function |
| :--- | :--- |
| **`coach_core.py`** | **Coach Mode.** Handles hint logic and terminal layout interaction with the "Cyber Coach." Enforces static directory instantiation limits on child processes, provides multi-tier tab-completion tracking across active directories, and maintains persistent readline history buffers for interactive input correction. |
| **`exploration_core.py`** | **Exploration Mode.** Manages challenge state and guided tutorials. |
| **`worker_node.py`** | Helper for sub-process execution and secure flag validation. |

### 🚩 Flag Lifecycle & Admin
Tools for generating content, tracking sanity states, and testing system integrity.

| Script | Function |
| :--- | :--- |
| **`verify_workspace.py`** | **Master Workspace Aggregator.** The ultimate sanity check. Automatically verifies package requirements, checks local paths, and runs asset validation sweeps in a single pass. It supersedes manual independent script execution. |
| **`generate_all_flags.py`** | Generates real/fake flags, challenge binaries, and challenges.json metadata. (Can be run independently or via verify_workspace.py). |
| **`validate_all_flags.py`** | **Master Validator.** Runs all 18 individual challenge validators to ensure total system integrity. (Can be run independently or via verify_workspace.py). |
| **`reset_environment.py`** | **Cleanup.** Purges generated binaries, flags, and temp files for a clean state. |

### 🌐 Web Interface
| Script | Function |
| :--- | :--- |
| **`start_web_hub.py`** | Launches the offline Flask web server (The Hub where students verify flags). |
| **`stop_web_hub.py`** | Gracefully shuts down the web hub. |

---

## 🛠️ Global Shell & Workspace Adjustments

To maximize terminal usability for students operating on the range, the master system template pushes baseline environment tweaks out natively via the skeleton profile setup.

*   **Persistent Tmux Tracking:** Global mouse interaction policies are baked into ~/.tmux.conf, /root/.tmux.conf, and /etc/skel/.tmux.conf. This enables click-to-focus pane switching, seamless layout resizing, and scrollback operations right out of the box.
*   **Up-Arrow History Buffering:** The custom terminal orchestration engine manually appends successful student submissions directly to the active readline history allocation loop, allowing users to hit the Up-Arrow to immediately correct fat-fingered string entries.
*   **Context-Aware Autocomplete:** The autocomplete library cross-references active subfolders in real time. Students can leverage Tab completion to discover file resources tucked deep inside specific challenge directories without breaking shell continuity.

---

## 🐳 Integrated Cyber Range Containers

In addition to the core 18 native challenges, the master range image deploys containerized sandbox applications configured for standalone execution.

### 🛒 OWASP Juice Shop
*   **Purpose:** Web Application Penetration Testing (SQLi, XSS, broken authentication scavenger hunt).
*   **Deployment:** Runs as a persistent background container mapped locally to port 3000.
*   **Access:** Provisioned with an automatic XFCE Desktop launcher pointing to http://localhost:3000.

### 🕵️‍♂️ Command Line Murder Mystery (clmystery)
*   **Purpose:** Linux command line literacy (mastering grep, awk, find, and filesystem filtering navigation).
*   **Deployment:** Locally built inside an isolated, transient Docker container layer.
*   **Access:** Hardcoded to a locked XFCE Desktop shortcut launcher. When double-clicked, it initiates a fresh terminal context forcing a clean docker run -it --rm clmystery:latest instance. This structure keeps students confined to a pure command line perimeter, protects the host filesystem, and resets completely upon exit.

---

## 🚀 Workflow for Contributors

1.  **Verify Workspace & Initialize Assets:**
    *   Always run this script first when kicking off a development cycle or validating local changes. It automatically runs asset generation (generate_all_flags.py), handles systemic variable parsing, checks environment dependencies, and executes the 18 distinct challenge validator scripts in a single master pipeline loop:
    ```bash
    ./verify_workspace.py
    ```

2.  **Compile the Web Architecture Layout:**
    *   Once your baseline workspace verification finishes clean and assets are properly placed, execute the web engine builder component to generate the browser interface deployment:
    ```bash
    ./web_version_admin/build_web_version
    ```

3.  **Build and Deploy Local Installation Snapshots:**
    *   Simulate an active student installation matrix or verify production range profiles by running your preferred target copy wrapper:
    ```bash
    ./copy_ccri_ctf.py
    ```

4.  **Clean Up (Pre-Commit):**
    *   Always clear out runtime state anomalies and temporary binaries before pushing your branch changes up to GitHub:
    ```bash
    ./reset_environment.py
    ```

---

## 🙌 Best Practices & Notes

*   **Security:** Admin-only JSON files (validation_unlocks*.json) must **never** be committed to public branches.
*   **Packaging:** .pyz files are the only runtime path for students; this bundles logic while preventing source code leaks.
*   **Environment:** This project assumes a Debian-based environment. Ensure python3-venv is used for local development to avoid conflicting with system-level packages.

---

## 📖 Contributing

Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide for branching strategies, PR workflows, and best practices for adding new challenges.