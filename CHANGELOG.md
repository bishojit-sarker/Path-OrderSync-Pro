# 📝 Changelog & Version History

All notable changes, bug fixes, and feature additions to **Smart Dropbox QC Batch Loader** are documented here.

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
