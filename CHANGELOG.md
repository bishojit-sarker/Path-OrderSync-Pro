# 📝 Changelog & Version History

All notable changes, bug fixes, and feature additions to **Smart Dropbox QC Batch Loader** are documented here.

---

## [v1.3.0] - 2026-11-02
### 🛡️ 3-Layer Storage Shield & Leftover Order Recovery:
- **🔍 Deep Disk Scanner (`[ 🔍 Find All Local Orders ]`):**
  - Directly scans all vendor directories in Dropbox for any leftover orders that are still hydrated or taking up physical disk space.
  - Automatically loads discovered local orders into the table and input box for immediate 1-click cleanup or inspection.
- **🕒 Persistent History Tracker & Live Badge (`[ 🕒 Leftover: X ]`):**
  - Tracks the sync state (local vs online) of every processed order in a local `history.json`.
  - Header badge displays the exact count of leftover local orders; highlights in amber/orange if forgotten orders exist.
  - Clicking the badge allows 1-click loading of all tracked leftover orders into the table for instant review or space release.
- **⚠️ Auto-Prompt Guard on New Batch Launch:**
  - When starting a new `Make Local` batch, the application detects if previous orders were left local on disk.
  - Prompts the user: *"Would you like to make previous orders Online-Only first to free up disk space?"*
  - Automatically frees previous orders in the background before downloading the new batch, eliminating storage bottlenecks.

---

## [v1.2.0] - 2026-11-02
### 🌟 New Features & Enhancements:
- **Single Order / Selected Order Online-Only (Individual Space Cleanup):**
  - Added **`[ ☁️ Make Selected Online ]`** button directly above the table.
  - Added right-click context menu on table rows:
    - 📂 Open in File Explorer
    - ☁️ Make this Order Online-Only (Instantly frees up disk space for single order)
    - 📥 Re-download (Make Local)
  - Users can now free disk space order-by-order as they finish QC, without waiting for the full 150-order batch to complete!
- **Smart Suffix Cleaner:**
  - Automatic removal of extra suffixes and tags attached to Order IDs (e.g. `#456883-P1` ➔ `#456883`, `#457000-E` ➔ `#457000`, `#456988-HI` ➔ `#456988`).
  - Works with hyphens, underscores, parts, and priority labels.
  - Formats cleanly into standard `#OrderID` list on deduplication.

---

## [v1.1.1] - 2026-11-02
### 🚀 Zero-Config Auto-Detection:
- **Automatic Dropbox Detection on Any PC:**
  - Reads official Dropbox configuration (`info.json`) across Business and Personal accounts.
  - Automatically identifies user-specific folder names (`Path Dropbox`, `Dropbox`, or Team accounts).

---

## [v1.1.0] - 2026-11-02
### 🌟 Major Upgrades:
- **Dual-Level Progress Tracking:**
  - Total Progress Percentage and order count (`Total Progress: XX% (X / Y Orders)`).
  - Single Order Progress Percentage and file count (`Current Order: #XXXXXX (Vendor) - XX% (X / Y Files)`).
- **Smart Order ID Deduplication & Cleanup:**
  - Real-time badge tracking total lines vs unique orders.
  - **`[ 🧹 Clean & Deduplicate ]`** button.
- **Multi-Vendor Split Order Support:**
  - Scans ALL vendor directories. If an order exists in multiple vendors, each vendor appears as its own row.
- **Batch Thread Controls (Pause / Resume / Stop):**
  - **`[ ⏸️ Pause ]` / `[ ▶️ Resume ]`** and **`[ ⏹️ Stop ]`**.

---

## [v1.0.1] - 2026-11-02
### 🐛 Bug Fixes:
- **Double Hash (`##`) Lookup Fix:** Fixed double `#` prefix in internal dictionary lookup.
- **Double-Click Row Selection:** Improved Treeview row identification on double-click.

---

## [v1.0.0] - 2026-11-02
### 🚀 Initial Release:
- Standalone Windows `.exe` desktop application.
- Multi-vendor scanning across `Path Dropbox`.
- 1-Click offline hydration and space recovery.
