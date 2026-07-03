# 🔓 Challenge 07: Extract from Binary

**Mission Briefing:**
A suspicious binary executable (`hidden_flag`) was recovered from a compromised system. Analysts believe it contains critical intelligence, but the data is buried deep within the compiled code, surrounded by thousands of lines of "garbage" data.

## 🧠 Intelligence Report
* **The Concept:** **Binaries** are compiled programs (0s and 1s). However, they often contain "hardcoded strings": plain text messages, variable names, or passwords stored directly inside the file.
* **The Lock:** The file is not a text file. Opening it in a standard editor will just show random symbols.
* **The Strategy:** **String Extraction**. We need a tool that ignores the binary machine code and prints only the sequences of human-readable characters.
* **The Warning:** The binary contains **decoy strings** mixed in with the real data. You must identify which one is the valid flag.

## 📝 Investigator’s Journal
*Notes from the field:*

> "They buried the message deep. I tried running the program, but it just crashed.
> 
> I know the flag is in there, but it's hidden amongst a mountain of random junk. You need to pull out *everything* readable and then filter aggressively for the pattern we care about (`CCRI-`)."

## 📂 Files in This Folder
* `hidden_flag`: The binary containing the embedded data.

---

## 🛠️ Tools & Techniques

This is a classic static analysis task. Use the pre-installed tools to isolate strings from the binary:

| Tool | Purpose | Usage Example |
| :--- | :--- | :--- |
| **strings** | The gold standard. Scans binary files for printable characters. | `strings hidden_flag` |
| **grep** | Filters output to find specific patterns. | `strings hidden_flag \| grep "CCRI-"` |
| **xxd** | Views the file as a Hex Dump (good for seeing context). | `xxd hidden_flag \| less` |

> 💡 **Tip:** The `strings` command outputs *a lot* of noise. You almost always want to pipe (`\|`) it into `grep` to find exactly what you are looking for. 

---

## 🏁 Flag Format
**`CCRI-AAAA-1111`**

Extract the strings, filter the noise, and identify the true flag.