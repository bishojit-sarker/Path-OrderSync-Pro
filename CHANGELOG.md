# 📝 Changelog & Version History

All notable changes, bug fixes, and feature additions to **Smart Dropbox QC Batch Loader** are documented here.

---

## [v1.6.0] - 2026-11-04
### 🚀 Path OrderSync Studio Overhaul, Smart File Review, Local Clean & Dynamic UI:
- **🎨 Brand Identity & Modern Header:**
  - Renamed application to **Path OrderSync Studio** with official tagline *"Smart Batch Order Sync & Space Optimizer"*.
  - Embedded infinity Dropbox brand logo into the app header and multi-resolution Windows executable icon.
  - Unified Dropbox Root path selector and hard drive space metrics into a single compact header row with a live `[ 🔄 Refresh ]` button.
- **🔔 Notification & Update Center:**
  - Replaced static check button with an interactive Notification Center (`🔔`).
  - Displays unread update badges, full release history organized by date, and one-click update installation with user confirmation prompt.
- **🧹 Dedicated Local Clean Tool (`[ 🧹 Local Clean ]`):**
  - Dedicated storage optimizer window showing only hydrated orders consuming physical hard drive space.
  - Multi-select checkboxes, real-time space calculation, and instant cloud-offloading to reclaim local disk space.
- **📜 Complete History Eraser (`[ 🗑️ Clean All History ]`):**
  - Added 1-click option inside History Tracker to permanently clear all local and online history records with a warning confirmation dialog.
- **📋 Toggle Drawer & Smart Duplicate Cleaner:**
  - Moved Paste Order IDs into a clean collapsible drawer toggled from the main toolbar (`[ 📋 Paste Order IDs ]`).
  - **Dynamic Button State**: `[ 🧹 Clean Duplicate ]` is **RED** and `[ ➕ Add to Sync List ]` is **DISABLED** whenever order text is edited. Once Clean Duplicate is clicked, button turns **GREEN** and Add to Sync List activates immediately.
- **🗑️ Dashboard Cleaner (`[ 🗑️ Clean Dashboard ]`):**
  - Added toolbar button to reset and clear all rows from the Sync List Dashboard with user confirmation.
- **🔍 Modern Pill Search Bar:**
  - Streamlined table header search into an ultra-modern pill container with inside `🔍` and integrated inside `✕` clear button.
- **☑️ Master Checkbox, Multi-Select & Copy Order IDs:**
  - Added table checkbox column with header master toggle (`☐` / `☑`) and keyboard Space bar support.
  - Enabled copying Order IDs to clipboard via `Ctrl + C` or right-click context menu.
- **🔍 Order Review & Smart Folder Filter (`[ 🔍 Order Review ]`):**
  - Interactive inspector for analyzing folder structure, subfolders, and file sizes before downloading.
  - Quick presets: `[ 🎯 QC Images Only (.tif, .psd, .jpg) ]` and `[ ⚡ Exclude RAW / Samples ]`.
  - Downloads only user-whitelisted files, saving substantial bandwidth and local disk space.
- **⚡ In-Cell Real-Time Progress Animation & Bottom Dock:**
  - Replaced static labels with live in-cell download progress indicators (`⏳ 15% (60/385 files)`) and row color highlights.
  - Modern bottom status dock featuring total progress bar, status badges, and global `[ ⏸️ Pause All ]` and `[ ⏹️ Stop All ]` controls.

---

## [v1.5.0] - 2026-11-03
### ⚡ Advanced Workflow Features & Deep Cloud Sync Reliability:
- **🖱️ Vendor Dropdown Smooth Mouse-Wheel Scrolling & Master Checkbox:**
  - Added smooth mouse-wheel scrolling (`<MouseWheel>`) from top to bottom across all vendor popup widgets.
  - Replaced separate "All" and "None" buttons with a single master checkbox `[ Select / Deselect All ]` that automatically syncs with individual vendor check states.
- **🔍 Scan Local Orders in Selected Vendors:**
  - Added `[ 🔍 Scan Local Orders ]` button in the main table toolbar.
  - Rapidly scans selected vendors in parallel to discover all orders and image files currently hydrated and consuming physical disk space.
  - Populates the Orders table with Order ID, Vendor, Sync Status, total files, and exact local disk size.
- **☁️ Multi-Row 'Make Online' (Bulk Space Reclaim):**
  - Upgraded table selection mode to `extended` for multi-row selection (Shift+Click, Ctrl+Click, or Drag).
  - Clicking `[ ☁️ Make Online ]` or right-clicking frees up disk space across all selected orders simultaneously.
- **📋 Collapsible / Toggle Sidebar for Order IDs:**
  - Replaced fixed left-hand space with a responsive collapsible sidebar.
  - Added `[ ◀ Hide Sidebar ]` / `[ 📋 Show Sidebar (Paste IDs) ]` button to maximize table and detail view.
- **➕ 'Add to Sync List' Button & Queue Submission:**
  - Added dedicated `[ ➕ Add to Sync List ]` button directly beside Clean & Deduplicate.
  - Parses pasted order IDs, checks current disk/cloud state across vendors, and queues them into the Process Table without immediately downloading.
- **🛡️ 100% Complete Local Hydration Fix (Zero Photoshop Hangs):**
  - Resolved partial file hydration issue where Photoshop froze while opening partially downloaded TIFF/PSD images.
  - Streams full files in parallel chunks and confirms removal of Windows `FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS` before declaring `✅ Local (Ready)`.

---

## [v1.4.0] - 2026-11-02
### ⚡ High-Speed Multi-Vendor Engine, Vendor Filter Dropdown, Storage Metrics & Full English UI:
- **🏢 Dynamic Vendor Dropdown & Multi-Select Filter:**
  - Automatically scans Dropbox root for all vendor directories on load and on path change.
  - Sleek dropdown button (`[ 🏢 Vendors: All (14) ▼ ]`) placed in the storage metrics bar.
  - **Single Vendor Isolation**: 1-click `[ Only ]` button next to each vendor immediately deselects all others and isolates only that vendor.
  - **Multi-Vendor Selection**: Toggle any combination of vendors via responsive checkboxes.
  - **Quick Controls**: `[ All ]`, `[ None ]`, `[ 🔄 Rescan ]`, and `[ ✕ Done ]` buttons.
  - **Instant Search**: Live search box inside the vendor dropdown to find vendors in large studio accounts.
  - **Strictly Scoped Execution**: Both `Make Local` and `Make Online` process only the active selected vendor(s), completely skipping unselected folders.
  - Persistent preference: Saves selected vendor filters across app restarts in `config.json`.
- **🔍 Live Search & Filter Bar:**
  - Added real-time Search Bar directly in the main QC table header with instant keystroke filtering (`<KeyRelease>`) by Order ID, Vendor, or Sync Status.
  - Added live Search Bar inside the **History Tracker Dialog** to filter historical and pending records on the fly.
  - One-click clear button (`✕`) to immediately reset filter and restore full list.
- **🌐 100% Full English UI (Zero Bengali Text):**
  - Completely translated all labels, dialogs, buttons, table headers, error prompts, and status messages into clean, professional English.
- **⚡ Blazing Fast Multi-Vendor Indexing & Parallel Hydration:**
  - Solved freezing and slowness when an order exists across multiple vendors.
  - **In-Memory Vendor Indexing**: Scans and maps 4,200+ orders across all vendors in ~15 milliseconds at batch start, reducing lookup complexity to instantaneous $O(1)$.
  - **Multi-Threaded Parallel Hydration**: Replaced sequential file streaming with `ThreadPoolExecutor(max_workers=8)` for concurrent file downloads, drastically reducing hydration time.
  - Combined atomic `attrib` operations to eliminate redundant subprocess calls.
  - Graceful cancellation and thread shutdown on `[ ⏹️ Stop ]` request.
- **💾 Live Storage Metrics & Disk Space Bar:**
  - Added dedicated **Live Storage Metrics Bar** displaying:
    - `💾 Drive Free Space`: Real-time free vs total space and percentage on the Dropbox drive (e.g. `💾 Drive (C:) Free Space: 59.9 GB / 389.7 GB (15% free)`).
    - `📦 Local QC Orders`: Exact physical disk footprint of all orders made local by the user (e.g. `📦 Local QC Orders: 2.45 GB (12 Orders on disk)`).
  - Live local disk footprint dynamically shown inside the top header badge: `[ ⚠️ Pending Local: X Orders (X.XX GB) ]`.
  - Added manual `[ 🔄 Refresh ]` button and automatic refresh triggers upon every local or online sync action.

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
