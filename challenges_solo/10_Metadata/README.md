# 🖼️ Challenge 10: Metadata Mystery

**Mission Briefing:**
You have recovered a suspicious image file (`capybara.jpg`) from a server used by the CryptKeepers. At first glance, it seems harmless—just a goofy animal photo. However, investigators believe a CryptKeeper operative embedded a flag inside the image’s **metadata** to pass it to a handler without raising suspicion.

## 🧠 Intelligence Report
* **The Concept:** **Metadata** is "data about data." For images, this includes camera settings, GPS coordinates, authors, and comments. 
* **The Lock:** The information isn't in the pixels; it's in the file header. Opening the image in a viewer won't reveal it.
* **The Warning:** The metadata contains **decoy flags** designed to mislead investigators. You must distinguish the real flag from the fakes.

## 📝 Investigator’s Journal
*Notes from the field:*

> "Metadata is often overlooked. They scrub the pixels but forget the headers. I've found critical intel hidden in `Comment`, `Artist`, or even `Copyright` tags before.
> 
> Run a full dump of the file properties. The specific tag doesn't matter as much as the content. Scan the entire output for the standard flag format (`CCRI-AAAA-1111`)."

## 📂 Files in This Folder
* `capybara.jpg`: The image hiding the data.

---

## 🛠️ Tools & Techniques

We need a tool that looks *at* the file properties, not *inside* the image pixel stream:

| Tool | Purpose | Usage Example |
| :--- | :--- | :--- |
| **exiftool** | The industry standard for reading/writing metadata. | `exiftool capybara.jpg` |
| **identify** | Part of ImageMagick; shows basic details. | `identify -verbose capybara.jpg` |
| **grep** | Use this to filter the output for the flag format. | `exiftool capybara.jpg \| grep "CCRI"` |

> 💡 **Tip:** Some metadata fields are obscure. Don't just look at the top few lines; scroll through the entire output.

---

## 🏁 Flag Format
**`CCRI-AAAA-1111`**

Extract the metadata, ignore the decoys, and find the true flag.