# ⚡ Smart Dropbox QC Batch Loader

[![Release](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078d7.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)]()

> **Automated Multi-Vendor Offline Sync & Cloud Storage Cleaner for E-Commerce Photo Quality Control (QC).**

Eliminates manual browser downloads and zip extractions for 100-150 daily completed orders. Seamlessly manages Dropbox Smart Sync (Hydration & Dehydration) across multiple vendors with zero disk bloat.

---

## 🌟 Key Features

1. **Zero-Friction Offline Hydration (`Make Local`):**
   - Automatically detects completed orders across all vendor folders (`cutout_edge`, `clipping_pix`, `path_subs`, `perfect_pixel`, etc.).
   - Downloads/hydrates files directly to disk using Windows Cloud Filter attributes (`attrib +P -U`) without browser downloads or ZIP extraction.
2. **Instant Space Recovery (`Free Up Space`):**
   - 1-Click space recovery reverts completed folders back to 0-byte online-only cloud placeholders (`attrib -P +U`).
   - Recover all disk space at the end of the day or order-by-order.
3. **Single Order Space Cleanup:**
   - Free up disk space order-by-order right after completing QC (`[ ☁️ Make Selected Online ]` or Right-Click menu) without waiting for the entire batch.
4. **Dual-Level Progress Tracking:**
   - **Total Progress Bar:** Tracks overall batch completion percentage (`XX% - X/Y Orders`).
   - **Single Order Progress Bar:** Tracks individual file hydration progress inside each order (`XX% - X/Y Files`).
5. **Intelligent Suffix Stripper & Deduplication:**
   - Cleans order tags like `#456883-P1`, `#457000-E`, `#456988-HI` into clean `#456883`, `#457000`, `#456988`.
   - Real-time line count vs unique order count badge + `[ 🧹 Clean & Deduplicate ]` button.
6. **Multi-Vendor Split Order Support:**
   - If a single order is divided between multiple vendors, all vendors appear as individual rows in the table with individual file counts and folders.
7. **Thread Controls:**
   - Interactive `[ ⏸️ Pause ]`, `[ ▶️ Resume ]`, and `[ ⏹️ Stop ]` buttons for safe execution control.
8. **Universal Auto-Detection:**
   - Automatically detects the user's Dropbox location on any computer via official Dropbox configuration (`info.json`) with zero manual setup.

---

## 🚀 Quick Setup & Installation

### Option A: Portable Standalone Executable
1. Download or copy the `QC Batch Loader` folder to your computer.
2. Double-click **`Install_Shortcut.bat`** to create a Desktop shortcut.
3. Double-click the **`QC Batch Loader`** icon on your Desktop.

### Option B: Run from Source (Python 3.10+)
```bash
# Clone the repository
git clone https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
cd Smart-Dropbox-QC-Batch-Loader

# Run the app directly
python app.py
```

---

## 📖 User Workflow

1. **Morning / Starting QC:**
   - Paste Order IDs into the left pane.
   - Click `[ 📥 1. Make Local (Ready for QC) ]`.
   - All files are downloaded locally with full progress feedback.
2. **Reviewing in Photoshop / Explorer:**
   - Double-click any order in the table or click `[ 📂 Open Folder ]` to open its `Completed` directory.
   - Once inspected, click `[ ☁️ Make Selected Online ]` to immediately recover hard drive space.
3. **End of Day Cleanup:**
   - Click `[ ☁️ 2. Free Up Space (Make Online-Only) ]` to revert all orders to 0-byte online placeholders.

---

## 🛠️ Auto-Update & GitHub Releases

- **Automatic Releases:** Pushing changes to `main` with a version tag triggers build packaging.
- **Publish Script:** Run `publish_update.bat` to automatically build, commit, and push updates.
- Check [CHANGELOG.md](CHANGELOG.md) for version history.
