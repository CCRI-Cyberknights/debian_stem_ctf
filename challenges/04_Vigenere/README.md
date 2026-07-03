# 🔐 Challenge 04: Vigenère Cipher

**Mission Briefing:**
You have recovered a scrambled message (`cipher.txt`) from an intercepted communication. Our analysts suspect it was encoded using the **Vigenère cipher**.

Unlike simple rotation ciphers (like ROT13), Vigenère uses a **keyword** to shift letters differently throughout the message. To break it, you need to know or guess that keyword.

## 🧠 Intelligence Report
* **The Cipher:** Vigenère (Polyalphabetic Substitution).
* **The Clue:** The system administrator left a hint in the logs: **"What is the opposite of `logout`?"**
* **The Requirement:** Decrypting Vigenère by hand is slow and error-prone. You will need to use a script or tool capable of handling the complex shifting logic.
* **The Warning:** The decrypted message lists **several potential flags**. You must identify the valid one.

**Your Goal:** Deduce the keyword from the clue, use the available tools to decrypt the message, and capture the flag.

## 📂 Files in This Folder
* `cipher.txt`: The encrypted message.

---

**🏁 Flag Format:** `CCRI-AAAA-1111`