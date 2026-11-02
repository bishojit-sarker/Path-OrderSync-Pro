# 📝 Changelog & Version History

All notable changes, bug fixes, and feature additions to **Smart Dropbox QC Batch Loader** are documented here.

---

## [v1.3.0] - 2026-11-02
### 📜 Persistent History Tracker (স্মার্ট হিস্ট্রি বা বকেয়া তালিকা):
- **📜 Dedicated History Tracker Manager Window (`HistoryTrackerDialog`):**
  - Clicking the header badge **`[ ⚠️ বকেয়া তালিকা: X টি লোকাল ]`** / **`[ 📜 বকেয়া তালিকা: ০ (Drive Clean) ]`** opens a full-featured management dashboard.
  - **Live Filter**: Easily toggle between `🔴 শুধু বকেয়া অর্ডার (Pending Local)` and `📋 সমস্ত হিস্ট্রি (All History)`.
  - **Real-time Statistics**: Displays live counts for `🔴 বকেয়া (Local)`, `🟢 মুক্ত (Online)`, and `📁 মোট রেকর্ড`.
  - **Color-Coded Status Tags**: Pending local orders highlighted with clear red/amber badges; online orders shown in green.
  - **Precision Timestamps**: Displays the exact date & time (`YYYY-MM-DD HH:MM AM/PM`) when each order was downloaded locally or freed.
- **⚡ 1-Click Operations in History Window:**
  - **`[ ⚡ সব বকেয়া অনলাইন করুন (Make ALL Pending Online) ]`**: 1-click batch online release for all pending local orders to instantly recover hard drive space.
  - **`[ ☁️ Make Selected Online ]`**: Free only the selected order(s) from the pending list.
  - **`[ 📋 Load to QC Table ]`**: Copies pending orders straight into the main QC input text box for immediate inspection.
  - **`[ 📂 Open Folder ]`**: Instant jump to any order folder in File Explorer (or double-click row).
  - **`[ 🗑️ Clear Completed History ]`**: Cleans up older finished online entries while keeping pending local orders completely safe.
- **🎯 100% Strict User Isolation (No Interference with Other Orders):**
  - Tracks ONLY the orders explicitly downloaded by this user through the app. Never touches or scans other Dropbox directories or orders worked on by other team members.

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
