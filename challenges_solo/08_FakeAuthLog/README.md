# 🕵️ Challenge 08: Fake Auth Log Investigation

**Mission Briefing:**
You have intercepted a suspicious system log file (`auth.log`) from a server controlled by the CryptKeepers. On Linux systems, this file records every login attempt, sudo command, and authentication event. It looks like a standard server log, except our analysts detected a pattern anomaly. A flag is hidden inside one of the entries, disguised as a system process to evade detection.

## 🧠 Intelligence Report
* **The Concept:** System logs follow a strict structure: `Date Hostname Process[PID]: Message`. 
* **The Anomaly:** The **PID** (Process ID) inside the square brackets `[]` is always a number (e.g., `sshd[1234]`).
* **The Strategy:** **Log Analysis**. We suspect the attacker tampered with the logs and replaced a numeric PID with text characters to hide their flag.
* **The Warning:** The log contains **decoy entries** designed to mislead investigators. You must verify which flag is the valid one.

## 📝 Investigator’s Journal
*Notes from the field:*

> "The log is filled with noise—thousands of SSH login attempts.
> 
> But I noticed something weird. Look closely at the Process IDs. They are supposed to be numbers, right? I saw some entries where the PID looked... off. Not numeric. That's where I started digging. Filter out the normal numbers to reveal the hidden strings, but check them carefully—I saw more than one odd entry."

## 📂 Files in This Folder
* `auth.log`: The simulated log file.

---

## 🛠️ Tools & Techniques

Use these pre-installed utilities to filter the logs and identify the pattern anomaly:

| Tool | Purpose | Usage Example |
| :--- | :--- | :--- |
| **grep** | Search for specific text patterns. | `grep "CCRI-" auth.log` |
| **awk** | Advanced filtering. Can check specific columns. | `awk '{print $5}' auth.log` |
| **less** | Scroll through the file manually. | `less auth.log` |
| **Regex** | Search for the pattern directly. | `grep -E "CCRI-[A-Z0-9]+" auth.log` |

> 💡 **Tip:** A normal log entry looks like this:
> `sshd[2910]: Accepted password...`
> 
> A suspicious entry might look like this:
> `sshd[FLAG]: Accepted password...`

---

## 🏁 Flag Format
**`CCRI-AAAA-1111`**

Filter the logs and find the non-numeric PID.