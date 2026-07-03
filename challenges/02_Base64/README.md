# 🧩 Challenge 02: Base64 Decode

**📡 Intercepted Transmission**
An encoded message has been intercepted from a compromised system. The file `encoded.txt` contains data obfuscated using **Base64**.

**Mission Briefing:**
**Base64 is NOT encryption.** It is a common encoding scheme used to represent binary data as text. It is frequently used in systems to encode credentials, configuration files, or data payloads for transmission.

## 🧠 Intelligence Report
* **The Signature:** Base64 strings consist of random alphanumeric characters and almost always end with one or two equals signs (`=`) as padding.
* **The Tools:** Linux has a built-in tool called `base64` specifically for reversing this. 
* **The Warning:** The decoded transmission lists **multiple flag candidates**. You must identify which one is the real flag.

**Your Goal:** Confirm the file matches the signature, then decode it to retrieve the flag.

## 📂 Files in This Folder
* `encoded.txt`: The intercepted Base64-encoded transmission.

---

**🏁 Flag Format:** `CCRI-AAAA-1111`