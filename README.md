# ⚡ Smart Dropbox QC Batch Loader

[![Release](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-0078d7.svg)](https://www.microsoft.com/windows)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader)

> **Automated Multi-Vendor Offline Sync & Cloud Storage Cleaner for E-Commerce Photo Quality Control (QC).**

---

### 🌐 Language Navigation / ভাষা নির্বাচন:
- [🇧🇩 বাংলা ডকুমেন্টেশন](#-বাংলা-ডকুমেন্টেশন)
- [🇬🇧 English Documentation](#-english-documentation)

---

# 🇧🇩 বাংলা ডকুমেন্টেশন

## 📌 পরিচিতি ও উদ্দেশ্য

**Smart Dropbox QC Batch Loader** হলো একটি Windows ডেস্কটপ অ্যাপ্লিকেশন যা ই-কমার্স ফটো এডিটিং স্টুডিওতে প্রতিদিনের ১০০-১৫০টি সম্পন্ন হওয়া অর্ডারের কোয়ালিটি কন্ট্রোল (QC) প্রক্রিয়াকে সম্পূর্ণ সহজ ও দ্রুততর করে। 

পূর্বে ড্রপবক্স ওয়েবসাইট থেকে প্রতিটি কমপ্লিট ফোল্ডার ডাউনলোড করতে হতো, যার ফলে প্রতিটি অর্ডার `.zip` ফাইল হয়ে যেত এবং বারবার আনজিপ করে ফটোশপে খুলতে প্রচুর সময় নষ্ট হতো। পাশাপাশি শত শত ভারী ইমেজ পিসিতে জমা হয়ে হার্ডডিস্কের জায়গা শেষ হয়ে যেত।

এই অ্যাপটি কোনো ব্রাউজার ডাউনলোড বা আনজিপ ছাড়াই সরাসরি উইন্ডোজের নিজস্ব ক্লাউড এপিআই ব্যবহার করে সেকেন্ডের মধ্যে ইমেজগুলোকে লোকাল মেমরিতে কিউসি করার উপযোগী করে দেয় এবং কিউসি শেষ হওয়ামাত্রই ১-ক্লিকে আবার ফাইলগুলোকে ক্লাউডে পাঠিয়ে হার্ডড্রাইভ সম্পূর্ণ খালি করে দেয়।

---

## 🌟 প্রধান প্রধান সুবিধাসমূহ (Key Features)

1. **জিরো-ডাউনলোড ও জিরো-আনজিপ (`Make Local`):**
   - ড্রপবক্সের যে কোনো ভেন্ডর ফোল্ডারে থাকা ফাইল ব্রাউজারে না ঢুকেই সরাসরি লোকাল মেমরিতে ডাউনলোড (Hydrate) করিয়ে নেয়। কোনো `.zip` ফাইল তৈরি হয় না।
2. **১-ক্লিকে হার্ডডিস্ক সম্পূর্ণ খালি করা (`Free Up Space`):**
   - দিনশেষে বা কাজ শেষে সব ফাইল এক ক্লিকে আবার মেঘের মতো `Online-Only (0 bytes)` হয়ে যায়। হার্ডডিস্ক ফুল হওয়ার কোনো ভয় নেই।
3. **সিঙ্গেল অর্ডার স্পেস রিকভারি:**
   - পুরো ১৫০টি অর্ডারের জন্য অপেক্ষা না করে, যেকোনো একটি অর্ডারের কিউসি শেষ হওয়ামাত্রই **`[ ☁️ Make Selected Online ]`** বোতাম বা রাইট-ক্লিক মেনু দিয়ে তাৎক্ষণিকভাবে ওই অর্ডারের মেমোরি খালি করা যায়।
4. **ডুয়েল পারসেন্টেজ ও লাইভ প্রগ্রেস বার:**
   - **মোট প্রগ্রেস বার:** মোট অর্ডারের কত শতাংশ শেষ হলো তা দেখায় (যেমন: `Total Progress: 60% (60/100 Orders)` )।
   - **সিঙ্গেল অর্ডার প্রগ্রেস বার:** নির্দিষ্ট অর্ডারের ভেতরের ফাইলগুলো কত শতাংশ লোকাল হলো তা রিয়েলটাইমে ফাইল সংখ্যা সহ দেখায় (যেমন: `Current Order: #456859 - 80% (16/20 Files)` )।
5. **অটোমেটিক সাফিক্স ক্লিনার ও ডুপ্লিকেট রিমুভার:**
   - অর্ডারের সাথে থাকা অতিরিক্ত ট্যাগ (যেমন: `#456883-P1`, `#457000-E`, `#456988-HI`) নিজে থেকেই ক্লিন করে মূল `#456883`, `#457000`, `#456988` তৈরি করে নেয়।
   - **`[ 🧹 Clean & Deduplicate ]`** বোতামে চাপ দিয়ে নিমিষেই তালিকা পরিষ্কার করা যায়।
6. **মাল্টি-ভেন্ডর স্প্লিট সাপোর্ট (Multi-Vendor Split):**
   - একটি অর্ডার যদি একাধিক ভেন্ডরের মধ্যে ভাগ করা থাকে (যেমন: ভেন্ডর A করল Clipping Path, ভেন্ডর B করল Retouching), টেবিলে প্রতিটি ভেন্ডরের জন্য আলাদা রো তৈরি হয় এবং যেটিতে ডাবল-ক্লিক করবেন সরাসরি সেই ভেন্ডরের ফোল্ডারটি ওপেন হবে।
7. **পজ, রেজ্যুম এবং স্টপ কন্ট্রোল (Pause / Resume / Stop):**
   - ব্যাচ চলাকালীন যেকোনো মুহূর্তে কাজ সাময়িক স্থগিত (`Pause`), পুনরায় চালু (`Resume`) বা বাতিল (`Stop`) করার পূর্ণ নিয়ন্ত্রণ।
8. **অন্য যেকোনো পিসির ড্রপবক্স স্বয়ংক্রিয়ভাবে চিনে নেওয়া (Universal Auto-Detection):**
   - অন্য যেকোনো কম্পিউটারে এই অ্যাপ চালু করলে নিজে থেকেই সেই পিসির ড্রপবক্স পাথ খুঁজে নেয়; ব্যবহারকারীকে কোনো পাথ ম্যানুয়ালি বসাতে হয় না।
9. **ইন-অ্যাপ অটো-আপডেট ইঞ্জিন (In-App Auto-Updater):**
   - গিটহাবে নতুন কোনো সংস্করণ প্রকাশ হলে অ্যাপ নিজে থেকেই নোটিফিকেশন দেবে এবং ১-ক্লিকে স্বয়ংক্রিয়ভাবে আপডেট হয়ে রিস্টার্ট নেবে।

---

## 🔄 এটি কীভাবে কাজ করে — সম্পূর্ণ Workflow

### ধাপ ১: ড্রপবক্স পাথ ও অর্ডার আইডি ইনপুট

```
┌────────────────────────────────────────────────────────────────────────┐
│  📁 Dropbox Root: C:\Users\Username\Path Dropbox            [Browse...]│
├────────────────────────────────────────────────────────────────────────┤
│  📋 Paste Order IDs:                Total: 120 lines | Unique: 85      │
│  ┌─────────────────────────────────┐                                  │
│  │ #456883-P1                      │                                  │
│  │ #457000-E                       │                                  │
│  │ #456988-HI                      │                                  │
│  │ #456883-P1 (ডুপ্লিকেট)          │                                  │
│  └─────────────────────────────────┘                                  │
│  [Clear]  [Paste from Clipboard]  [ 🧹 Clean & Deduplicate ]          │
└────────────────────────────────────────────────────────────────────────┘
```

- অ্যাপ ওপেন হলে কম্পিউটারের ড্রপবক্স পাথ নিজে থেকেই বসে যাবে।
- টিস্তা বা এক্সেল থেকে অর্ডার আইডি কপি করে পেস্ট করুন।
- **`[ 🧹 Clean & Deduplicate ]`** চাপলে অতিরিক্ত সাফিক্স কেটে ফ্রেশ ইউনিক আইডি তৈরি হবে।

---

### ধাপ ২: কিউসি প্রস্তুতকরণ (`Make Local`)

```
┌────────────────────────────────────────────────────────────────────────┐
│  [ 📥 1. Make Local (Ready for QC) ]   [ ☁️ 2. Free Up Space ]         │
│  [ ⏸️ Pause ]                          [ ⏹️ Stop ]                     │
├────────────────────────────────────────────────────────────────────────┤
│  Total Progress:  [████████████░░░░░░░░] 60% (60 / 100 Orders)          │
│  Single Order:    [████████████████░░░░] 80% (16 / 20 Files)           │
│                   Syncing #456859 under cutout_edge - 0016.tif...      │
└────────────────────────────────────────────────────────────────────────┘
```

- **`[ 📥 1. Make Local ]`** বাটনে চাপ দিন।
- ব্যাকগ্রাউন্ডে অ্যাপটি ড্রপবক্সের সব ভেন্ডর ফোল্ডার স্ক্যান করে ফাইলগুলোকে সরাসরি পিসির লোকাল মেমরিতে ডাউনলোড করিয়ে ফেলবে।

---

### ধাপ ৩: টেবিল থেকে সরাসরি ফাইল পরিদর্শন ও সিঙ্গেল অর্ডার রিলিজ

```
┌────────────────────────────────────────────────────────────────────────┐
│  📊 Orders & Sync Status:    [ ☁️ Make Selected Online ] [ 📂 Open ]   │
├───────────┬──────────────────────┬──────────────────────┬──────────────┤
│ Order ID  │ Vendor               │ Sync Status          │ Files        │
├───────────┼──────────────────────┼──────────────────────┼──────────────┤
│ #456859   │ perfect_pixel        │ ✅ Local (Ready)     │ 17           │
│ #456876   │ Khandoker_graphics   │ ✅ Local (Ready)     │ 1            │
│ #456879   │ path_subs            │ ☁️ Online-Only       │ 2            │
└───────────┴──────────────────────┴──────────────────────┴──────────────┘
```

- **ফোল্ডার ওপেন করতে:** টেবিলে যেকোনো অর্ডারের ওপর **ডাবল-ক্লিক** করুন। সাথে সাথে উইন্ডোজ ফাইল এক্সপ্লোরারে সেই অর্ডারের `Completed` ফোল্ডার খুলে যাবে।
- **সিঙ্গেল অর্ডার স্পেস খালি করতে:** কাজ শেষ হওয়া অর্ডারে ক্লিক করে **`[ ☁️ Make Selected Online ]`** চাপুন অথবা রাইট-ক্লিক মেনু থেকে "Make Online-Only" দিন। সাথে সাথে ওই অর্ডারের ফাইল ক্লাউড মোডে ফিরে যাবে এবং পিসির মেমরি খালি হবে।

---

### ধাপ ৪: ব্যাকএন্ড ইন্টারনাল প্রসেস ফ্লোচার্ট

```
[ 📥 Make Local ] ক্লিক
          │
          ▼
┌─ ১. সাফিক্স ক্লিন ও ইউনিক ফিল্টার ──────────┐
│  #456883-P1 থেকে 456883 বের করে ডুপ্লিকেট বাদ দেয়।│
└─────────────────────────────────────────┘
          │
          ▼
┌─ ২. মাল্টি-ভেন্ডর স্ক্যানার ───────────────────┐
│  Path Dropbox-এর সব ভেন্ডর ডিরেক্টরি স্ক্যান    │
│  করে OrderID/Completed ফোল্ডার খুঁজে বের করে।    │
└─────────────────────────────────────────┘
          │
          ▼
┌─ ৩. উইন্ডোজ ক্লাউড ফিল্টার পিন (attrib +P -U) ──┐
│  ফোল্ডার ও ফাইলগুলোকে Pinned চিহ্নিত করে যাতে   │
│  ড্রপবক্স এগুলোকে লোকাল ড্রাইভ মেমরিতে আনে।      │
└─────────────────────────────────────────┘
          │
          ▼
┌─ ৪. ইনস্ট্যান্ট হাইড্রেশন ও ফাইল রিড ────────────┐
│  ফাইলের প্রথম অংশ রিড করে ড্রপবক্স থেকে তাৎক্ষণিক │
│  ফুল-ডাউনলোড সম্পন্ন করায় ও প্রগ্রেস আপডেট দেয়।  │
└─────────────────────────────────────────┘
          │
          ▼
   ✅ Local (Ready for QC in Photoshop)
```

---

## 💻 সেটআপ — প্রথমবার কীভাবে শুরু করবেন

### সাধারণ ব্যবহারকারীদের জন্য (জিরো কোডিং):
1. প্রজেক্ট ফোল্ডারটি আপনার কম্পিউটারে রাখুন (যেমন: `E:\QC Batch Loader`)।
2. ফোল্ডারের ভেতর থাকা **`Install_Shortcut.bat`** ফাইলে ডাবল-ক্লিক করুন।
3. সাথে সাথে আপনার ডেস্কটপে **`QC Batch Loader`** নামে শর্টকাট তৈরি হয়ে যাবে।
4. ডেস্কটপ শর্টকাটে ডাবল-ক্লিক করলেই অ্যাপ ওপেন হয়ে যাবে!

### ডেভেলপারদের জন্য (Python 3.10+):
```bash
# গিট ক্লোন করুন
git clone https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
cd Smart-Dropbox-QC-Batch-Loader

# সরাসরি রান করুন
python app.py
```

---

## 📁 ফোল্ডার স্ট্রাকচার

```
Smart-Dropbox-QC-Batch-Loader/
├── app.py                   ← মূল অ্যাপ্লিকেশন ও GUI (সব কোড এখানে)
├── QC_Batch_Loader.exe      ← ডাবল-ক্লিকযোগ্য স্ট্যান্ডঅ্যালোন এক্সিকিউটেবল (.exe)
├── Install_Shortcut.bat     ← ১-ক্লিকে ডেস্কটপ শর্টকাট তৈরির স্ক্রিপ্ট
├── publish_update.bat       ← ১-ক্লিকে গিটহাবে অটো-বিল্ড ও রিলিজ পুশ স্ক্রিপ্ট
├── config.json              ← অটো-ডিটেক্টেড ড্রপবক্স পাথ সংরক্ষিত ফাইল
├── USER_GUIDE.md            ← বিস্তারিত ইউজার গাইড
├── CHANGELOG.md             ← ভার্সন হিস্ট্রি ও আপডেট লগ
└── README.md                ← এই ডকুমেন্টেশন ফাইল
```

---

## 🤖 AI দিয়ে কোড আপডেট করার নির্দেশনা (নন-কোডারদের জন্য)

যদি আপনি নন-কোডার হন এবং AI (যেমন Antigravity, ChatGPT, Claude) ব্যবহার করে এই অ্যাপে নতুন কোনো ফিচার যোগ করতে চান, নিচের ধাপগুলো অনুসরণ করুন:

### ধাপ ১: কোন ফাইল পরিবর্তন করতে হবে তা বুঝুন
সম্পূর্ণ অ্যাপ্লিকেশনের সোর্স কোড মূলত একটি ফাইলে রয়েছে:
```
app.py
```

### ধাপ ২: AI-কে পরিষ্কার নির্দেশনা দিন
AI-কে বলার সময় নিচের মতো বাস্তব উদাহরণ দিয়ে বলুন:
```text
উদাহরণ ১: "app.py ফাইলে একটি বাটন যোগ করো যেটা দিয়ে Not Found হওয়া 
অর্ডারগুলোর তালিকা এক ক্লিকে ক্লিপবোর্ডে কপি করা যাবে।"

উদাহরণ ২: "টেবিলে ফাইলের সাইজ কত MB সেটা দেখানোর জন্য নতুন একটি কলাম যোগ করো।"

উদাহরণ ৩: "প্রসেস শেষ হলে একটি সাউন্ড অ্যালার্ট বাজাও।"
```

### ধাপ ৩: পরিবর্তন করার আগে সতর্কতা
1. **ব্যাকআপ নিন:** পরিবর্তন করার আগে `app.py` ফাইলের একটি কপি রাখুন।
2. **টেস্ট করুন:** পরিবর্তন শেষে রান করে দেখুন কোনো এরর আসে কিনা।
3. **গিটহাবে প্রকাশ করুন:** সবকিছু ঠিক থাকলে ফোল্ডারের **`publish_update.bat`** ফাইলে ডাবল-ক্লিক করলেই নতুন `.exe` তৈরি হয়ে গিটহাবে আপডেট চলে যাবে!

### ধাপ ৪: AI-কে দেওয়ার জন্য গুরুত্বপূর্ণ সিস্টেম সামারি
AI-কে নিচের তথ্যগুলো দিলে সে নিখুঁত কোড তৈরি করতে পারবে:
- **প্রজেক্ট:** Python + Tkinter/TTK দিয়ে তৈরি Windows 10/11 ডেস্কটপ অ্যাপ।
- **মূল ফাইল:** `app.py`
- **ড্রপবক্স প্রযুক্তি:** Windows Cloud Filter (`attrib +P -U` এবং `attrib -P +U`)।
- **থিম:** Dark Theme (`#1e1e2e` ব্যাকগ্রাউন্ড, ব্লু ও গ্রিন অ্যাকসেন্ট)।
- **কনফিগ:** `config.json` ফাইলে ড্রপবক্স রুট পাথ সংরক্ষিত হয়।

---

## ⚠️ AI Coderদের জন্য গুরুত্বপূর্ণ কারিগরি সতর্কতা

> **নতুন AI Coderদের জন্য অপরিহার্য নিয়মাবলী:**

### ১. কোড স্ট্রাকচার ও ক্লাস ডিজাইন
- মূল ক্লাস `QCBatchLoaderApp` (`tk.Tk` থেকে ইনহেরিট করা)।
- কোনো ভারী এক্সটার্নাল লাইব্রেরির ওপর নির্ভর করবেন না; অ্যাপটি সম্পূর্ণ স্ট্যান্ডার্ড পাইথন লাইব্রেরি ও Tkinter দিয়ে তৈরি যাতে যেকোনো পিসিতে ডিপেন্ডেন্সি ছাড়াই চলে।

### ২. Windows Cloud Filter আর্কিটেকচার
- ফাইল অফলাইন/লোকাল করার জন্য: `attrib +P -U "{folder}\*.*" /s` এবং ইনস্ট্যান্ট হাইড্রেশনের জন্য প্রথম ১KB রিড (`open(fp, 'rb').read(1024)` )।
- ফাইল ফ্রি/অনলাইন-অনলি করার জন্য: `attrib -P +U "{folder}\*.*" /s`।
- সরাসরি কোনো লো-লেভেল লক হ্যান্ডেল ব্যবহার করবেন না, উইন্ডোজের `attrib` কমান্ড শতভাগ নির্ভরযোগ্য।

### ৩. মাল্টি-ভেন্ডর স্ক্যানিং লজিক
- `_find_all_vendor_matches(base_path, order_id)` ড্রপবক্সের সবকটি ভেন্ডর ফোল্ডারে স্ক্যান করে। প্রথম ভেন্ডর পেলেই লুপ ভাঙবেন না (`break` দেবেন না), কারণ একই অর্ডার একাধিক ভেন্ডরে স্প্লিট থাকতে পারে।

### ৪. থ্রেডিং ও থ্রেড-সেফ UI আপডেট
- সব ভারী ড্রপবক্স অপারেশন ব্যাকগ্রাউন্ড `threading.Thread`-এ চালাতে হবে।
- UI ফ্রিজ রোধে `self.pause_event.wait()` এবং `self.stop_requested` ফ্ল্যাগ নিয়মিত চেক করতে হবে।
- ব্যাকগ্রাউন্ড থ্রেড থেকে সরাসরি উইজেট মেথড কল করার সময় সতর্ক থাকুন।

### ৫. অটো-আপডেট ইঞ্জিন
- উইন্ডোজে চালু থাকা অবস্থায় `.exe` সরাসরি মোছা বা ওভাররাইট করা যায় না। তাই অ্যাপটি প্রথমে রানিং এক্সিকিউটেবলকে `.old` নামে রিনেম করে, নতুন ভার্সন ডাউনলোড করে এবং পুরাতনকে রিস্টার্টের সময় মুছে দেয়। এই সোয়াপিং লজিক কখনোই ভাঙবেন না।

### ৬. কোড টেস্ট করার চেকলিস্ট
কোড এডিট করার পর:
1. `python app.py` দিয়ে চালিয়ে দেখুন কোনো সিনট্যাক্স এরর আছে কিনা।
2. অর্ডার আইডি পেস্ট করে `Make Local` চালিয়ে দেখুন প্রগ্রেস বার কাজ করছে কিনা।
3. টেবিলের রো-তে ডাবল-ক্লিক করে ফোল্ডার খুলছে কিনা দেখুন।
4. `Make Selected Online` বোতাম দিয়ে একক অর্ডারের স্পেস খালি হচ্ছে কিনা পরীক্ষা করুন।

---

## ❓ সাধারণ সমস্যা এবং সমাধান (FAQ)

| সমস্যা | কারণ | তাৎক্ষণিক সমাধান |
|---|---|---|
| **❌ Not Found দেখাচ্ছে** | ভেন্ডর এখনও ফাইল আপলোড করেনি বা ড্রপবক্স সিঙ্ক হয়নি। | ড্রপবক্সে ভেন্ডর ফোল্ডারে গিয়ে অর্ডার আইডি চেক করুন। |
| **ফোল্ডার ওপেন হচ্ছে না** | ড্রপবক্স রুট পাথ ভুল সিলেক্ট করা আছে। | উপরে `Browse...` বাটনে চাপ দিয়ে সঠিক ড্রপবক্স ফোল্ডারটি দেখিয়ে দিন। |
| **ডাবল ক্লিকে ফোল্ডার খুলছে না** | ফোল্ডারটি এখনও কম্পিউটারের ড্রাইভে তৈরি হয়নি। | আগে `Make Local` বাটনে চাপ দিয়ে ফাইলগুলো প্রস্তুত করে নিন। |
| **ডাউনলোড অনেক স্লো** | ড্রপবক্স ডেস্কটপ অ্যাপ ব্যাকগ্রাউন্ডে পজ করা আছে। | টাস্কবার থেকে ড্রপবক্স আইকন দেখে নিশ্চিত করুন ড্রপবক্স সিঙ্ক চালু আছে। |
| **অটো-আপডেট কাজ করছে না** | ইন্টারনেট সংযোগ নেই বা গিটহাব এপিআই ব্লকেড। | ম্যানুয়ালি গিটহাব রিলিজ পেজ থেকে নতুন `QC_Batch_Loader.exe` ডাউনলোড করে নিন। |

---

<br><br>

---

# 🇬🇧 English Documentation

## 📌 Overview & Purpose

**Smart Dropbox QC Batch Loader** is a specialized Windows desktop utility designed for e-commerce photo retouching and editing production houses handling 100-150 completed orders daily.

Previously, quality control (QC) operators had to navigate to the Dropbox web interface for every single order and download folders manually. This process caused immense operational friction:
- Web downloads generate `.zip` archives that require repetitive manual extraction.
- Excessive cognitive load and context switching between order management platforms and Adobe Photoshop.
- Storing hundreds of heavy, high-resolution TIFF/PSD files rapidly exhausts local SSD storage.

This application eliminates web downloads and manual unzipping entirely. Utilizing native Windows Cloud Filter APIs, it hydrates (downloads) images directly into local disk memory for instant QC inspection, and reverts them back to 0-byte online-only cloud placeholders with a single click once inspection is complete.

---

## 🌟 Key Highlights & Features

1. **Zero-Download & Zero-Zip Offline Hydration (`Make Local`):**
   - Directly fetches completed orders from any vendor directory (`cutout_edge`, `clipping_pix`, `path_subs`, `perfect_pixel`, etc.) into local memory without touching a web browser.
2. **1-Click Hard Drive Space Recovery (`Free Up Space`):**
   - Reverts all completed order files back into 0-byte cloud placeholders (`attrib -P +U`) at the end of the day. Zero disk storage bloat.
3. **Single Order Space Cleanup:**
   - Free up disk space order-by-order right after completing QC using the **`[ ☁️ Make Selected Online ]`** button or the right-click context menu, without waiting for the full 150-order batch.
4. **Dual-Level Progress Tracking:**
   - **Total Progress Bar:** Tracks overall batch completion percentage (`Total Progress: 60% (60/100 Orders)`).
   - **Single Order Progress Bar:** Tracks individual file hydration progress inside each order in real time (`Current Order: #456859 - 80% (16/20 Files)`).
5. **Intelligent Suffix Stripper & Deduplication:**
   - Automatically sanitizes order tags like `#456883-P1`, `#457000-E`, `#456988-HI` into clean `#456883`, `#457000`, `#456988`.
   - Real-time line count vs unique order count badge + **`[ 🧹 Clean & Deduplicate ]`** button.
6. **Multi-Vendor Split Order Support:**
   - If an order is divided between multiple vendors (e.g., clipping path by Vendor A, retouching by Vendor B), all vendors appear as individual rows with independent file counts and one-click folder jumping.
7. **Execution Controls (Pause / Resume / Stop):**
   - Interactive buttons to safely pause, resume, or abort long-running batch synchronization processes.
8. **Universal Auto-Detection:**
   - Automatically detects the user's Dropbox location on any computer via official Dropbox configuration (`info.json`) with zero manual setup.
9. **In-App Auto-Updater:**
   - Automatically checks GitHub Releases on startup and provides 1-click self-updating without manual file transfers.

---

## 🔄 How It Works — Complete Workflow

### Step 1: Dropbox Path & Order ID Input

```
┌────────────────────────────────────────────────────────────────────────┐
│  📁 Dropbox Root: C:\Users\Username\Path Dropbox            [Browse...]│
├────────────────────────────────────────────────────────────────────────┤
│  📋 Paste Order IDs:                Total: 120 lines | Unique: 85      │
│  ┌─────────────────────────────────┐                                  │
│  │ #456883-P1                      │                                  │
│  │ #457000-E                       │                                  │
│  │ #456988-HI                      │                                  │
│  │ #456883-P1 (duplicate)          │                                  │
│  └─────────────────────────────────┘                                  │
│  [Clear]  [Paste from Clipboard]  [ 🧹 Clean & Deduplicate ]          │
└────────────────────────────────────────────────────────────────────────┘
```

- Dropbox root path is automatically detected and populated.
- Paste Order IDs copied from Tista or Excel.
- Click **`[ 🧹 Clean & Deduplicate ]`** to strip suffixes and remove duplicates.

---

### Step 2: Preparing for QC (`Make Local`)

```
┌────────────────────────────────────────────────────────────────────────┐
│  [ 📥 1. Make Local (Ready for QC) ]   [ ☁️ 2. Free Up Space ]         │
│  [ ⏸️ Pause ]                          [ ⏹️ Stop ]                     │
├────────────────────────────────────────────────────────────────────────┤
│  Total Progress:  [████████████░░░░░░░░] 60% (60 / 100 Orders)          │
│  Single Order:    [████████████████░░░░] 80% (16 / 20 Files)           │
│                   Syncing #456859 under cutout_edge - 0016.tif...      │
└────────────────────────────────────────────────────────────────────────┘
```

- Click **`[ 📥 1. Make Local ]`**.
- The app scans all vendor folders and downloads the files directly to disk with live dual progress bars.

---

### Step 3: Inspection & Single Order Cleanup

```
┌────────────────────────────────────────────────────────────────────────┐
│  📊 Orders & Sync Status:    [ ☁️ Make Selected Online ] [ 📂 Open ]   │
├───────────┬──────────────────────┬──────────────────────┬──────────────┤
│ Order ID  │ Vendor               │ Sync Status          │ Files        │
├───────────┼──────────────────────┼──────────────────────┼──────────────┤
│ #456859   │ perfect_pixel        │ ✅ Local (Ready)     │ 17           │
│ #456876   │ Khandoker_graphics   │ ✅ Local (Ready)     │ 1            │
│ #456879   │ path_subs            │ ☁️ Online-Only       │ 2            │
└───────────┴──────────────────────┴──────────────────────┴──────────────┘
```

- **Open Folder:** Double-click any row to open the `Completed` directory in Windows File Explorer.
- **Single Order Space Cleanup:** When QC is finished for an order, click **`[ ☁️ Make Selected Online ]`** or right-click and select "Make Online-Only".

---

### Step 4: Internal Backend Flowchart

```
[ 📥 Make Local ] Clicked
          │
          ▼
┌─ 1. Suffix Cleaning & Deduplication ────────┐
│  Extracts base order number (e.g. 456883)   │
│  and filters out duplicate entries.         │
└─────────────────────────────────────────────┘
          │
          ▼
┌─ 2. Multi-Vendor Scanner ───────────────────┐
│  Scans all vendor folders in Path Dropbox   │
│  to resolve order directories and Completed │
│  subfolders.                                │
└─────────────────────────────────────────────┘
          │
          ▼
┌─ 3. Cloud Filter Pinning (attrib +P -U) ────┐
│  Marks folders and files as Pinned to       │
│  instruct Dropbox to keep files on device.  │
└─────────────────────────────────────────────┘
          │
          ▼
┌─ 4. Instant Hydration & File Stream Read ───┐
│  Reads initial bytes of each placeholder to │
│  trigger immediate background hydration.    │
└─────────────────────────────────────────────┘
          │
          ▼
   ✅ Local (Ready for QC in Photoshop)
```

---

## 💻 Setup & Installation Guide

### For QC Operators (Zero Coding Required):
1. Copy the `QC Batch Loader` folder to your computer.
2. Double-click **`Install_Shortcut.bat`** (this creates a desktop shortcut).
3. Double-click the **`QC Batch Loader`** icon on your Desktop.

### For Developers (Python 3.10+):
```bash
git clone https://github.com/bishojit-sarker/Smart-Dropbox-QC-Batch-Loader.git
cd Smart-Dropbox-QC-Batch-Loader
python app.py
```

---

## 📁 Folder Structure

```
Smart-Dropbox-QC-Batch-Loader/
├── app.py                   ← Main application & GUI source code
├── QC_Batch_Loader.exe      ← Standalone double-clickable Windows executable
├── Install_Shortcut.bat     ← 1-Click desktop shortcut installer
├── publish_update.bat       ← 1-Click auto-build and GitHub push script
├── config.json              ← Stores auto-detected Dropbox configuration
├── USER_GUIDE.md            ← Detailed user manual
├── CHANGELOG.md             ← Release notes and version history
└── README.md                ← This documentation file
```

---

## 🤖 Updating Code with AI (Guide for Non-Coders)

If you are a non-coder using an AI coding assistant (like Antigravity, ChatGPT, Claude) to add features, follow these steps:

### Step 1: Identify the File to Change
The entire application logic resides in a single file:
```
app.py
```

### Step 2: Provide Clear Actionable Prompts
```text
Example 1: "Add a button to export all Not Found orders to the clipboard."
Example 2: "Add a column in the table to display total folder size in MB."
Example 3: "Play an alert sound when a batch finishes processing."
```

### Step 3: Safety Checklist
1. **Backup:** Keep a copy of `app.py` before making edits.
2. **Test:** Run the app to confirm there are no syntax or runtime errors.
3. **Publish:** Double-click **`publish_update.bat`** to compile the `.exe` and push updates to GitHub automatically!

---

## ⚠️ Technical Guardrails for AI Coders

### 1. Code Architecture
- Main application class: `QCBatchLoaderApp` (subclassed from `tk.Tk`).
- Uses standard library Python and Tkinter for maximum zero-dependency compatibility across Windows systems.

### 2. Windows Cloud Filter Integration
- To pin / make local: `attrib +P -U "{folder}\*.*" /s` combined with a stream read (`open(fp, 'rb').read(1024)`).
- To unpin / make online-only: `attrib -P +U "{folder}\*.*" /s`.
- Do not hold open low-level file handles with exclusive locks; use `attrib` commands which work reliably across all Windows 10/11 versions.

### 3. Multi-Vendor Scanning
- `_find_all_vendor_matches(base_path, order_id)` scans across all vendor directories. Do not break early after finding one vendor, as split orders exist across multiple vendors.

### 4. Threading & Thread-Safe UI Updates
- All disk and cloud sync operations must run in daemon threads.
- Periodically check `self.pause_event.wait()` and `self.stop_requested` to ensure responsive UI controls.

### 5. Auto-Updater Engine
- Windows prevents deleting or overwriting running executables. The updater renames `QC_Batch_Loader.exe` to `QC_Batch_Loader.exe.old`, downloads the new binary, spawns it, and cleans up `.old` upon launch.

---

## ❓ Troubleshooting & FAQs

| Issue | Cause | Solution |
|---|---|---|
| **❌ Not Found** | Vendor has not uploaded files yet or folder name differs. | Check the vendor folder in Dropbox manually. |
| **Folder Doesn't Open** | Dropbox root path is incorrect. | Click `Browse...` and select the correct Dropbox root directory. |
| **Slow Sync** | Dropbox client is paused. | Check the Windows taskbar and ensure Dropbox sync is active. |
| **Auto-Update Fails** | Network restriction or GitHub blocked. | Download the latest `QC_Batch_Loader.exe` directly from GitHub Releases. |

---

## 📄 License & Attribution
Developed and maintained by **Bisshojit Sarker** ([GitHub](https://github.com/bishojit-sarker)).  
© 2026 Path Edits. All rights reserved.
