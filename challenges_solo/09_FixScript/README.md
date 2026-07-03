# 🐍 Challenge 09: Fix the Flag!

**Mission Briefing:**
You recovered a Python script (`broken_flag.py`) that was supposed to generate the agency's daily authentication code. However, the script is malfunctioning. It runs without crashing, but the number it produces at the end is incorrect. It seems the developer made a typo in the math logic.

## 🧠 Intelligence Report
* **The Concept:** **Logic Errors**. Unlike "Syntax Errors" (which stop the code from running), logic errors happen when the code runs perfectly but performs the wrong operation (e.g., adding instead of multiplying).
* **The Lock:** The final four digits of the flag are calculated mathematically. Currently, that calculation is incorrect.
* **The Strategy:** **Debugging**. You must open the source code, find the line performing the math, and fix the operator.
* **The Warning:** You must modify the source code to get the correct result.

## 📝 Investigator’s Journal
*Notes from the field:*

> "I ran the script, but the flag it spit out was rejected by the system.
> 
> I took a peek at the source code. It looks like a simple math mistake. The comments in the code say it's supposed to *multiply* the values to get the final checksum, but I think I saw a different operator in there.
> 
> You'll need to open the file, find the bug, fix it, and run it again."

## 📂 Files in This Folder
* `broken_flag.py`: The buggy Python script.

---

## 🛠️ Tools & Techniques

Use your preferred text editor and the Python 3 interpreter to debug and execute the script:

| Tool | Purpose | Usage Example |
| :--- | :--- | :--- |
| **nano** | Terminal text editor. Use this to locate and fix the bug. | `nano broken_flag.py` |
| **python3** | Executes the Python script to verify your fix. | `python3 broken_flag.py` |
| **cat** | Quickly view the code structure without editing. | `cat broken_flag.py` |

> 💡 **Tip:** Look closely at the math symbols in the code:
> * `+` (Add)
> * `-` (Subtract)
> * `*` (Multiply)
> * `/` (Divide)
> 
> One of these operators is incorrect based on the script's intended logic.

---

## 🏁 Flag Format
**`CCRI-AAAA-1111`**

Fix the code, run the script, and get the correct flag.