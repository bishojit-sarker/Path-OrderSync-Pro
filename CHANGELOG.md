# 📝 Changelog & Version History

All notable changes, bug fixes, and feature additions to **Smart Dropbox QC Batch Loader** are documented here.

## [v1.8.0] - 2026-11-06

### 🚀 Real-Time Dual Progress Engine, Responsive Multi-Resolution Layout & Advanced Cloud Hydration:
- **Dual Progress Indicators for Files & File Size:**
  - Transformed the `Files` and `File Size` columns into live download progress indicators following the `( downloaded / total )` format.
  - **Cloud / Initial State:** `Files` displays `0 / {total_files}` (e.g. `0 / 13`) and `File Size` displays `0 B / {total_size}` (e.g. `0 B / 373.45 MB`).
  - **Real-Time Hydration State:** Both file counter and byte accumulator stream continuously in real-time as data arrives from Dropbox (e.g. `1 / 13` files and `142.50 MB / 373.45 MB`).
  - **Local / QC Ready State:** Automatically transitions to complete totals upon full hydration (e.g. `13 / 13` files and `373.45 MB / 373.45 MB`).
- **Ultra-Smooth 128KB Chunk-Level Real-Time Hydration Engine:**
  - High-speed multithreaded chunk streaming with real-time decimal precision (`● Syncing 15.4%`, `● Syncing 68.2%` ... up to `● Local`).
  - Thread-safe byte synchronization allowing continuous live progress tracking even for single gigantic multi-gigabyte PSD/TIFF files (e.g. 1.62 GB single file orders).
  - 25 FPS UI throttle ensures buttery smooth visual feedback without CPU spiking or interface freezes.
- **Fully Responsive Multi-Resolution Layout (Maximize & Resize):**
  - Enabled proportional column auto-stretching (`stretch=True`) across all 8 dashboard columns, completely eliminating trailing white space gaps when maximized.
  - Redesigned search bar and wrapped header action buttons (`Make Online`, `Scan Local`, `Clean Dash`, `Review`) in an auto-fitting container, preventing button squishing or clipping on any screen resolution.
  - Optimized drawer width and column minimum bounds to guarantee `Open`, `Make Online`, and `Make Local` columns remain fully visible without clipping.
- **Independent Direct-Action Row Controls:**
  - Dedicated `Make Local` and `Make Online` buttons side-by-side on every row for 1-click single-order hydration or cloud offloading without mode switching.
  - Dedicated in-row `📁 Open` action button to open specific order folders directly in Windows File Explorer.
- **Integrated Pixel-Perfect Rounded Checkboxes:**
  - Native PIL supersampling generates smooth rounded checkboxes directly inside the `Order ID` column (`[✓] Order ID ˅` in header and row items), perfectly aligned with row checkboxes and zero visual jitter.
- **Dedicated Settings Center & Instant Dark/Light Theme Switching:**
  - Non-blocking Settings dialog with custom Gear icon, automatic Dropbox root discovery, and instantaneous smooth theme mode switching (zero screen blink).
- **High-Performance 5-Tier Cloud Dehydration & Storage Optimizer:**
  - 5-tier offload architecture combining Windows Shell COM verbs, Cloud Files API (`cldapi.dll`), recursive directory unpinning, attribute clearing, and shell change notifications for guaranteed instant zero-byte disk space reclamation.

---

## [v1.7.0] - 2026-11-05

### 🎨 Brand Identity, Modern UI Redesign & Settings Center:
- **Clean Modern Interface:** Complete CustomTkinter light and dark theme overhaul with rounded pill cards.
- **Dedicated Settings Center:** Non-blocking Settings dialog with custom Gear icon, automatic Dropbox root discovery, and instantaneous smooth theme mode switching (zero screen blink).
- **Direct 1-Click Open Dropbox:** Added `📂 Open Dropbox` pill button directly on the dashboard control strip.
- **Individual In-Row Open Button:** Added dedicated `📁 Open` column for each table row so users can open the order folder directly from each line.
- **Separate Dedicated Action Columns:** Separated the action buttons into two independent columns (`Make Local` and `Make Online`) side-by-side on every dashboard row, allowing 1-click execution of downloading or offloading to cloud without toggling.
- **Modern Integrated Rounded Checkboxes:** Seamlessly integrated the selection checkboxes directly inside the `Order ID` column as anti-aliased rounded rectangles generated dynamically via PIL supersampling beside `Order ID ˅` in the header and `#Order_ID` in rows, eliminating separate ugly text-character columns. Fixed header checkbox positioning using custom ttk style layout to place the master checkbox on the left side of `Order ID ˅` aligned with all row items.
- **Order Total File Size Column:** Replaced `Disk Size` with `File Size` in the dashboard table. Clicking `+ Add to sync list` now immediately calculates and surfaces the actual total file size of all files in the order folder (e.g. `1.62 GB`) regardless of whether the files are currently cloud-only or local on disk.
- **Dual Progress Indicators for Files & File Size:** Transformed the "Files" and "File Size" columns into live download progress indicators following the `( downloaded / total )` format (e.g. Files shows `0 / 13` and File Size shows `0 B / 373.45 MB` for cloud orders). During downloading, real-time chunk streaming feeds live byte and file counter progress directly into both columns (e.g. `1 / 13` files and `142.50 MB / 373.45 MB`), dynamically progressing up to `13 / 13` and `373.45 MB / 373.45 MB` upon full hydration.
- **Fully Responsive Multi-Resolution Layout (Maximize & Resize):** Enabled responsive column stretching (`stretch=True`) across all Treeview columns with proportional auto-balancing, eliminating blank white space when the window is maximized. Compacted drawer width and right card header action buttons into a flexible container so all toolbar buttons (`Review`, `Clean Dash`, `Scan Local`, `Make Online`) and table columns (`Open`, `Make Online`, etc.) stay perfectly visible without clipping or squishing across all standard and high-DPI display resolutions.
- **Dynamic Sync Status & Smooth Real-Time Decimal Progress (%):** Redesigned the `Sync Status` column to match the pill badge aesthetic (`● Local` in soft pastel green, `● Syncing X.X%` in soft sky blue with live per-chunk hydration progress, and `● Cloud Only` in soft neutral gray). Replaced coarse integer jumps with smooth, granular floating-point progression (`0.1%`, `0.2%`, `0.3%`... up to `99.9%` and `● Local`) synchronized in real time with the `File Size` column (e.g. `654.91 MB / 1.53 GB`). Reduced chunk size to 128 KB and optimized UI throttle to 25 FPS for fluid decimal counter animation across both single and batch hydration.
- **Table Footer Progress Bar & Compact Action Dock:** Moved Total Orders status counter and full-width progress bar directly beneath the table inside the main dashboard card (as requested), removed the redundant Single Order bar, and activated real-time progress bar animations using native CustomTkinter `.set()` float fractions.
- **Robust Shell Dehydration Engine:** Fixed PowerShell path resolution using `.NET System.IO.Path` APIs to handle paths containing `#` flawlessly, triggering native Windows Explorer `Make online-only` context menu verbs cleanly.
- **High-Performance Multi-Tier Cloud Dehydration Engine:** Upgraded `free_up_space_cfapi` with a 5-tier architecture:
  1. Windows Shell COM context menu automation (`Free up space` / `Make online-only`) executed directly on folders and files.
  2. Windows Cloud Files API (`cldapi.dll`) with exclusive oplock retry and background eviction (`CfOpenFileWithOplock`, `CfSetPinState`, `CfDehydratePlaceholder`).
  3. Recursive directory-level unpinning via `CreateFileW` with `FILE_FLAG_BACKUP_SEMANTICS`.
  4. Native attribute clearing (`attrib -P +U`) with a guaranteed 4-second timeout to prevent UI hangs.
  5. Shell change notifications (`SHChangeNotify`) to immediately switch green local checkmarks back to blue cloud placeholders in Windows Explorer.
- **Live Update Indicators:** Automatic alert with pulsating notification bell and red dot (`🔴`) on Settings button when a new release is detected.
- **New Brand Assets:** High-definition brand logo and multi-size Windows app icon.

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
