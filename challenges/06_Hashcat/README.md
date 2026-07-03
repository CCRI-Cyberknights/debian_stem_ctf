# 🔓 Challenge 06: Hashcat ChainCrack

**Mission Briefing:**
You have intercepted 3 encrypted archive segments from a data exfiltration attempt. Each segment is locked with a different password.

However, we also found a file (`hashes.txt`) containing the MD5 hashes of those passwords. You must reverse these hashes to regain access to the contents.

## 🧠 Intelligence Report
* **The Lock:** Three separate ZIP files located in the `segments/` directory (`part1.zip`, `part2.zip`, `part3.zip`).
* **The Keys:** The passwords are obfuscated behind MD5 hashes. You must crack them to unlock the archives.
* **The Warning:** Once reassembled, the data will yield **multiple potential flags**. Only one is valid.
* **The Strategy:** 
    1. **Crack:** Reverse the hashes using the provided wordlist.
    2. **Unlock:** Use the revealed passwords to extract the segments.
    3. **Assemble:** The extracted files are fragments. Combine them to reconstruct the final flag list.

**Your Goal:** Execute the crack, unlock the segments, and reassemble the intelligence.

## 📂 Files in This Folder
* `hashes.txt`: The list of target MD5 hashes.
* `wordlist.txt`: A list of candidate passwords.
* `segments/`: A folder containing the encrypted ZIP files.

---

**🏁 Flag Format:** `CCRI-AAAA-1111`