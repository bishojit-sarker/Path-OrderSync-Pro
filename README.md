# ⚡ Smart Dropbox QC Batch Loader

[![Release](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078d7.svg)](https://www.microsoft.com/windows)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader)

> **Automated Multi-Vendor Offline Sync & Cloud Storage Cleaner for E-Commerce Photo Quality Control (QC).**

---

### 🌐 Language Navigation / ভাষা নির্বাচন:
- [🇬🇧 English Documentation](#-english-documentation)
- [🇧🇩 বাংলা ডকুমেন্টেশন](#-বাংলা-ডকুমেন্টেশন)

---

# 🇬🇧 English Documentation

## 📌 Overview
In high-volume e-commerce photo editing workflows, teams handle 100-150 completed orders daily. Downloading folders from the Dropbox web interface causes massive friction:
- Every folder download creates a `.zip` archive that must be manually extracted.
- Heavy reliance on Adobe Photoshop slows down routine specification inspections.
- Keeping hundreds of high-resolution images locally fills up hard drive storage.

**Smart Dropbox QC Batch Loader** solves this by automating Dropbox Smart Sync (Hydration & Dehydration) across multiple vendor directories using native Windows Cloud Filter attributes. It enables zero-download, zero-zip inspection with 1-click cloud space recovery.

---

## 🌟 Key Features

1. **Zero-Friction Offline Hydration (`Make Local`):**
   - Automatically scans all vendor directories (`cutout_edge`, `clipping_pix`, `path_subs`, `perfect_pixel`, etc.) for matching Order IDs.
   - Downloads/hydrates files directly to disk via Windows Cloud Filter attributes (`attrib +P -U`) without web downloads or ZIP extraction.
2. **Instant Space Recovery (`Free Up Space`):**
   - 1-Click space recovery reverts completed folders back to 0-byte online-only cloud placeholders (`attrib -P +U`).
   - Recover all disk space at the end of the day with a single button.
3. **Single Order Space Cleanup:**
   - Free up disk space order-by-order right after completing QC (`[ ☁️ Make Selected Online ]` or Right-Click menu) without waiting for the full batch.
4. **Dual-Level Progress Tracking:**
   - **Total Progress Bar:** Tracks overall batch completion percentage (`XX% - X/Y Orders`).
   - **Single Order Progress Bar:** Tracks individual file hydration progress inside each order (`XX% - X/Y Files`).
5. **Intelligent Suffix Stripper & Deduplication:**
   - Automatically strips tags like `#456883-P1`, `#457000-E`, `#456988-HI` into clean `#456883`, `#457000`, `#456988`.
   - Real-time line count vs unique order count badge + `[ 🧹 Clean & Deduplicate ]` button.
6. **Multi-Vendor Split Order Support:**
   - If an order is divided between multiple vendors (e.g. clipping by Vendor A, retouching by Vendor B), all vendors appear as individual rows in the table with individual file counts and folders.
7. **Thread Controls:**
   - Interactive `[ ⏸️ Pause ]`, `[ ▶️ Resume ]`, and `[ ⏹️ Stop ]` buttons for safe execution control.
8. **Universal Auto-Detection:**
   - Automatically detects the user's Dropbox location on any computer via official Dropbox configuration (`info.json`) with zero manual setup.
9. **In-App Auto-Updater:**
   - Automatically checks GitHub Releases on launch and offers 1-click updates whenever a new version is published.

---

## 🚀 Installation & Quick Start

### For General QC Users:
1. Download or copy the `QC Batch Loader` folder to your computer.
2. Double-click **`Install_Shortcut.bat`** to create a Desktop shortcut.
3. Double-click the **`QC Batch Loader`** icon on your Desktop.

### For Developers (Run from Source):
```bash
# Clone the repository
git clone https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
cd Smart-Dropbox-QC-Batch-Loader

# Run the app directly
python app.py
```

---

## 📖 Daily Workflow

1. **Morning / Starting QC:**
   - Paste Order IDs into the left pane.
   - Click `[ 📥 1. Make Local (Ready for QC) ]`.
   - Files are downloaded locally with full dual progress feedback.
2. **Reviewing in Photoshop / Explorer:**
   - Double-click any order in the table or click `[ 📂 Open Folder ]` to open its `Completed` directory.
   - Once inspected, click `[ ☁️ Make Selected Online ]` to immediately recover hard drive space.
3. **End of Day Cleanup:**
   - Click `[ ☁️ 2. Free Up Space (Make Online-Only) ]` to revert all orders to 0-byte online placeholders.

---

# 🇧🇩 বাংলা ডকুমেন্টেশন

## 📌 পরিচিতি ও সফটওয়্যারের উদ্দেশ্য
প্রতিদিন ১০০-১৫০টি সম্পন্ন হওয়া অর্ডারের ইমেজ ড্রপবক্স ওয়েবসাইট থেকে ডাউনলোড করে কিউসি (QC) করা অত্যন্ত সময়সাপেক্ষ ও জটিল:
- ব্রাউজার থেকে ফোল্ডার ডাউনলোড করলেই ড্রপবক্স সেটিকে `.zip` বানিয়ে দেয়, যা বারবার এক্সট্রাক্ট করতে হয়।
- শত শত ভারী ছবি পিসিতে জমা হতে হতে হার্ডডিস্কের ফাঁকা জায়গা দ্রুত শেষ হয়ে যায়।
- ভারী ফটোশপে প্রতিটি ফাইল ওপেন করতে গিয়ে সময় অপচয় হয়।

**Smart Dropbox QC Batch Loader** এই সমস্যাটির একটি স্থায়ী সমাধান। এটি কোনো ডাউনলোড বা আনজিপ ছাড়া সরাসরি উইন্ডোজের ইন্টারনাল ক্লাউড এপিআই ব্যবহার করে ছবিগুলোকে মুহূর্তেই লোকাল মেমরিতে কিউসি করার উপযোগী করে দেয় এবং কাজ শেষ হওয়ামাত্রই ১-ক্লিকে আবার হার্ডড্রাইভ সম্পূর্ণ খালি করে দেয়।

---

## 🌟 প্রধান প্রধান সুবিধাসমূহ

1. **জিরো-ডাউনলোড ও জিরো-আনজিপ (`Make Local`):**
   - ড্রপবক্সের যে কোনো ভেন্ডর ফোল্ডারে (`cutout_edge`, `clipping_pix`, `path_subs` ইত্যাদি) থাকা কমপ্লিট ফাইল কোনো ব্রাউজার ছাড়াই সরাসরি লোকাল মেমরিতে ডাউনলোড করিয়ে নেয়।
2. **১-ক্লিকে হার্ডডিস্ক খালি করা (`Free Up Space`):**
   - দিনশেষে বা কাজ শেষে সব ফাইল এক ক্লিকে আবার মেঘের মতো `Online-Only (0 bytes)` হয়ে যায়। কোনো হার্ডডিস্ক মেমোরি নষ্ট হয় না।
3. **সিঙ্গেল অর্ডার স্পেস রিকভারি:**
   - পুরো ১৫০টি অর্ডারের জন্য অপেক্ষা না করে, যেকোনো একটি অর্ডারের কিউসি শেষ হওয়ামাত্রই **`[ ☁️ Make Selected Online ]`** বা রাইট-ক্লিক মেনু দিয়ে সাথে সাথে ওই অর্ডারের মেমোরি খালি করা যায়।
4. **ডুয়েল পারসেন্টেজ ও প্রগ্রেস বার:**
   - **টোটাল প্রগ্রেস বার:** মোট অর্ডারের কত শতাংশ শেষ হলো তা দেখায় (`Total Progress: XX%`).
   - **সিঙ্গেল অর্ডার প্রগ্রেস বার:** নির্দিষ্ট অর্ডারের ফাইলগুলো কত শতাংশ লোকাল হলো তা রিয়েলটাইমে ফাইল সংখ্যা সহ দেখায়।
5. **অটোমেটিক সাফিক্স ক্লিনার ও ডুপ্লিকেট রিমুভার:**
   - অর্ডারের সাথে থাকা অতিরিক্ত ট্যাগ (যেমন: `#456883-P1`, `#457000-E`, `#456988-HI`) নিজে থেকেই ক্লিন করে স্ট্যান্ডার্ড `#456883`, `#457000`, `#456988` বানিয়ে নেয়।
   - **`[ 🧹 Clean & Deduplicate ]`** বাটনে চাপ দিয়ে নিমেষেই তালিকা পরিষ্কার করা যায়।
6. **মাল্টি-ভেন্ডর স্প্লিট সাপোর্ট:**
   - একটি অর্ডার যদি একাধিক ভেন্ডরের মধ্যে ভাগ করা থাকে, টেবিলে প্রতিটি ভেন্ডরের জন্য আলাদা রো (Row) তৈরি হয় এবং যেটিতে ডাবল-ক্লিক করবেন সরাসরি সেই ভেন্ডরের ফোল্ডারটি ওপেন হবে।
7. **পজ, রেজ্যুম এবং স্টপ কন্ট্রোল:**
   - ব্যাচ প্রসেস চলাকালীন যে কোনো মুহূর্তে **`[ ⏸️ Pause ]`**, **`[ ▶️ Resume ]`**, এবং **`[ ⏹️ Stop ]`** করা যায়।
8. **অন্য যে কোনো পিসির ড্রপবক্স স্বয়ংক্রিয়ভাবে চিনে নেওয়া (Auto-Detection):**
   - অন্য যে কোনো কম্পিউটারে এই অ্যাপ চালু করলে নিজে থেকেই সেই পিসির ড্রপবক্স লোকেশন খুঁজে নেয়; ব্যবহারকারীকে কোনো পাথ টাইপ করতে হয় না।
9. **ইন-অ্যাপ অটো-আপডেট ইঞ্জিন:**
   - গিটহাবে নতুন কোনো সংস্করণ প্রকাশ হলে অ্যাপ নিজে থেকেই নোটিফিকেশন দেবে এবং ১-ক্লিকে স্বয়ংক্রিয়ভাবে আপডেট হয়ে রিস্টার্ট নেবে।

---

## 🚀 ইন্সটলেশন ও সেটআপ নির্দেশিকা

### সাধারণ ব্যবহারকারীদের জন্য:
1. `QC Batch Loader` ফোল্ডারটি আপনার কম্পিউটারে কপি করুন।
2. ফোল্ডারের ভেতর থাকা **`Install_Shortcut.bat`** ফাইলে ডাবল-ক্লিক করুন (এতে আপনার ডেস্কটপে শর্টকাট তৈরি হবে)।
3. ডেস্কটপের **`QC Batch Loader`** আইকনে ডাবল-ক্লিক করলেই অ্যাপ ওপেন হয়ে যাবে!

---

## 📋 প্রতিদিন কাজের সহজ ৩টি ধাপ

| ধাপ | করণীয় | ফলাফল |
| :--- | :--- | :--- |
| **১. কাজের শুরুতে** | টিস্তা থেকে অর্ডার আইডি পেস্ট করে **`[ 📥 1. Make Local ]`** চাপুন। | সব ফাইল অফলাইন মেমরিতে ডাউনলোড হয়ে ফটোশপে দেখার জন্য প্রস্তুত হবে। |
| **২. কিউসি চলাকালীন** | টেবিলে ডাবল ক্লিক করে ছবি চেক করুন। কাজ শেষে **`[ ☁️ Make Selected Online ]`** চাপুন। | সাথে সাথে ওই অর্ডারের ফাইলগুলো ক্লাউড মোডে ফিরে যাবে এবং পিসির মেমোরি ফাঁকা হবে। |
| **৩. দিনশেষে** | সারাদিনের কিউসি শেষে **`[ ☁️ 2. Free Up Space ]`** বোতামে চাপ দিন। | সারাদিনের সব অর্ডারের মেমোরি এক ক্লিকে খালি হয়ে যাবে। |

---

## 👨‍💻 ডেভেলপারদের জন্য গিটহাব আপডেট নিয়ম

ভবিষ্যতে কোনো কোড বা ফিচার আপডেট করলে:
- ফোল্ডারে থাকা **`publish_update.bat`** ফাইলে ডাবল-ক্লিক করুন।
- এটি স্বয়ংক্রিয়ভাবে নতুন `.exe` কম্পাইল করবে এবং সরাসরি আপনার GitHub রিপোজিটরিতে Push করে দেবে।
- সাথে সাথে স্টুডিওর সব কর্মীর পিসির অ্যাপে অটো-আপডেট নোটিফিকেশন চলে যাবে!

---

## 📄 লাইসেন্স ও কপিরাইট
© 2026 [Bisshojit Sarker](https://github.com/bishojit-sarker). All rights reserved.
