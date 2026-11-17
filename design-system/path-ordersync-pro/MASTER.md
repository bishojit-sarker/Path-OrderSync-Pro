# 📐 Path OrderSync Pro — Unified Design System
> **Document Type:** Master Design System (Global Source of Truth)  
> **Status:** Active / Production Standard  
> **Target Platform:** Windows 10 & 11 Desktop (CustomTkinter + Python)  
> **Standard:** `ui-ux-pro-max` (WCAG 2.2 AA/AAA, Material Design 3, Microsoft Fluent / Apple HIG)  
> **Version:** 2.0.0  
> **Last Updated:** 2026-11-13  

---

## 1. Brand Identity & Logo Guidelines

### 1.1 Brand Philosophy
**Path OrderSync Pro** হলো একটি হাই-স্পিড ই-কমার্স ফটো কোয়ালিটি কন্ট্রোল (QC) এবং ড্রপবক্স ক্লাউড সিঙ্ক অটোমেশন টুল। এর ভিজ্যুয়াল ভাষা হবে:
- **Clean & Modern Flat:** অপ্রয়োজনীয় থ্রিডি বা ভারী গ্রেডিয়েন্ট পরিহার করে স্পষ্ট ও সমতল লেআউট।
- **Reliable & Professional:** এন্টারপ্রাইজ গ্রেডের নির্ভরযোগ্যতা ও স্থায়িত্ব।
- **Cloud-Centric & Action-Driven:** ফাইল সিঙ্ক ও স্টোরেজ অপ্টিমাইজেশনকে পরিষ্কার কালার ল্যাঙ্গুয়েজে ফুটিয়ে তোলা।

### 1.2 Logo Preservation & Asset Specifications
অ্যাপ্লিকেশনটির বর্তমান অফিসিয়াল লোগো কোনো ধরনের পরিবর্তন বা বিকৃতি ছাড়া মূল ব্র্যান্ড অ্যাসেট হিসেবে অক্ষুণ্ণ থাকবে।

| Asset File | Native Dimensions | Primary Usage | Render Size (UI) | Clear Space |
| :--- | :--- | :--- | :--- | :--- |
| `assets/logo_header.png` | 128 × 128 px (PNG) | Main App Top Header | 34 × 34 px (`CTkImage`) | 8px min surrounding gap |
| `assets/logo_64.png` | 64 × 64 px (PNG) | Modals / Dialog Headers | 32 × 32 px | 8px min surrounding gap |
| `assets/logo_1024.png` | 1024 × 1024 px (PNG) | About Window / Splash / Docs | Scaled (e.g. 96 × 96 px) | 16px min surrounding gap |
| `assets/app_icon.ico` | Multi-size ICO | Window Icon, Taskbar, Executable | Native OS scaling | OS Defined |

#### লোগো ব্যবহারের অলঙ্ঘনীয় নিয়ম:
1. **Aspect Ratio Lock:** লোগোর অনুপাত সর্বদা ১:১ (বর্গাকার) থাকবে; কখনো স্ট্রেচ বা স্কুইশ করা যাবে না।
2. **Direct Background Placement:** লোগোটি সরাসরি হেডার ক্যানভাস বা কার্ডের উপর স্বচ্ছ ব্যাকগ্রাউন্ড সহ বসবে; এর চারপাশে কৃত্রিম বর্ডার বা ড্রপ শ্যাডো যুক্ত করা যাবে না।
3. **Coexistence:** হেডারের বাম পাশে লোগো, তার ঠিক ডানে অ্যাপের টাইটেল (`Path OrderSync Pro`) এবং ভার্সন পিল (`v1.9.0`) একটি সুষম গ্রুপ হিসেবে বিন্যস্ত থাকবে।

---

## 2. Brand Color Palette (Canonical 5 Swatches)

ব্যবহারকারীর নির্ধারিত ৫টি ব্র্যান্ড কালারের সুনির্দিষ্ট ভূমিকা এবং এক্সেসিবিলিটি ম্যাট্রিক্স:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 🎨 CANONICAL BRAND COLOR MATRIX                                        │
├─────────┬───────────┬──────────────────┬─────────────────┬─────────────┤
│ Palette │ Hex Code  │ Role & Semantics │ Light Mode Use  │ Dark Mode   │
├─────────┼───────────┼──────────────────┼─────────────────┼─────────────┤
│ Primary │ #292194   │ Deep Royal Navy  │ Main Brand CTA  │ Hero Accent │
│ Accent  │ #F6CE4C   │ Sunburst Amber   │ Warning / Pause │ Caution Tag │
│ Support │ #9B93EE   │ Lavender Violet  │ Meta & Badges   │ Soft Accent │
│ Second  │ #7BB5EF   │ Sky Blue (Cloud) │ Cloud / Free Up │ Cyan Glow   │
│ Danger  │ #E66360   │ Coral Red        │ Stop / Delete   │ Destructive │
└─────────┴───────────┴──────────────────┴─────────────────┴─────────────┘
```

### ২.১ কালার কনট্রাস্ট ও এক্সেসিবিলিটি ভ্যালিডেশন (WCAG 2.2 Standard)
`ui-ux-pro-max` নিয়ম অনুযায়ী প্রতিটি ফোরগ্রাউন্ড ও ব্যাকগ্রাউন্ড পেয়ারের কনট্রাস্ট রেশিও কঠোরভাবে পরীক্ষিত:

| Color Token | Foreground | Background | Contrast Ratio | WCAG 2.2 Rating | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary CTA** | `#FFFFFF` | `#292194` | **12.07 : 1** | 🟢 **AAA Pass** | "Make Local" Primary Button |
| **Accent / Pause**| `#181825` | `#F6CE4C` | **11.58 : 1** | 🟢 **AAA Pass** | "Pause / Resume" Button |
| **Secondary CTA**| `#0B1B36` | `#7BB5EF` | **7.92 : 1** | 🟢 **AAA Pass** | "Free Up Space" Cloud Button |
| **Supporting Tag**| `#1E1B4B` | `#9B93EE` | **5.94 : 1** | 🟢 **AAA Pass** | History / Order Tag Pill |
| **Danger CTA** | `#FFFFFF` | `#E66360` | **3.32 : 1** | 🟢 **AA Large Pass**| "Stop" / "Delete" Action Button |
| **Danger Text** | `#B91C1C` | `#FFFFFF` | **6.47 : 1** | 🟢 **AAA Pass** | Light Mode Inline Error Text |
| **Success Text** | `#047857` | `#FFFFFF` | **5.48 : 1** | 🟢 **AAA Pass** | Light Mode "Local / Ready" Text |
| **Main Body Text**| `#0F172A` | `#FFFFFF` | **17.85 : 1** | 🟢 **AAA Pass** | Card Content / Table Primary Text |
| **Muted Text** | `#475569` | `#FFFFFF` | **7.58 : 1** | 🟢 **AAA Pass** | Captions / Subtitles |

---

## 3. Light & Dark Semantic Theme Tokens

কোডের হার্ডকোডেড ৮৫টি হেক্স কালার সম্পূর্ণরূপে বর্জন করে নিচের সুনির্দিষ্ট থিম টোকেন সিস্টেম ব্যবহার করতে হবে।

### ৩.১ Light Theme Tokens ("Ice Slate & Royal Navy")
```python
THEME_LIGHT = {
    "id": "light",
    "name": "Light Theme",
    
    # Canvas & Cards
    "bg_canvas": "#EBF4FB",        # Soft ice-blue background
    "bg_card": "#FFFFFF",          # Pure white cards
    "bg_input": "#FFFFFF",         # Form fields & input boxes
    "border": "#D1E1EE",           # Crisp light structural border
    "border_focus": "#292194",     # Primary focus ring
    
    # Typography
    "text_main": "#0F172A",        # Slate-900 (High contrast, 17.8:1)
    "text_muted": "#475569",       # Slate-600 (Accessible secondary, 7.5:1)
    "text_disabled": "#94A3B8",    # Slate-400 (Disabled states)
    
    # Brand Action Colors (From 5 Swatches)
    "primary": "#292194",          # Deep Royal Navy (CTA)
    "primary_hover": "#1E1870",    # Darkened Navy on hover
    "primary_text": "#FFFFFF",     # White text on Primary (12.0:1)
    
    "secondary": "#7BB5EF",        # Sky Blue (Cloud Sync)
    "secondary_hover": "#5A9FE6",  # Darker Sky Blue
    "secondary_text": "#0B1B36",   # Deep Slate Navy for 7.9:1 contrast
    
    "accent": "#F6CE4C",           # Sunburst Amber (Pause/Warning)
    "accent_hover": "#E5BC36",     # Muted Gold hover
    "accent_text": "#181825",      # Dark text on Gold (11.5:1)
    
    "supporting": "#9B93EE",       # Periwinkle / Lavender
    "supporting_hover": "#857BE8", # Deep Periwinkle
    "supporting_text": "#1E1B4B",  # Deep Indigo text (5.9:1)
    
    "danger": "#E66360",           # Coral Red (Destructive)
    "danger_hover": "#D14D4A",     # Darker Coral hover
    "danger_text": "#FFFFFF",      # White text on Danger button
    "danger_inline": "#B91C1C",    # Accessible Red for normal text (6.4:1)
    
    "success": "#047857",          # Emerald-700 (High contrast green, 5.4:1)
    "success_hover": "#065F46",    # Darker Green
    "success_bg": "#DEF7EC",       # Soft pastel green pill
    "success_text": "#046C4E",     # Pill text
    
    # Table & List Components
    "tree_bg": "#FFFFFF",
    "tree_heading_bg": "#F8FAFC",
    "tree_heading_fg": "#475569",
    "tree_row_even": "#FFFFFF",
    "tree_row_odd": "#F8FAFC",
    "tree_row_select": "#E0E7FF",
    "tree_row_select_fg": "#1E1B4B",
    
    # Status Row Tints (Accessible Pastels)
    "status_local_bg": "#DEF7EC",
    "status_local_fg": "#046C4E",
    "status_sync_bg": "#E1EFFE",
    "status_sync_fg": "#1E429F",
    "status_cloud_bg": "#F1F5F9",
    "status_cloud_fg": "#334155",
    "status_notfound_bg": "#FDE8E8",
    "status_notfound_fg": "#991B1B",
}
```

### ৩.২ Dark Theme Tokens ("Midnight Slate & Royal Glow")
```python
THEME_DARK = {
    "id": "dark",
    "name": "Dark Theme",
    
    # Canvas & Cards
    "bg_canvas": "#0C1024",        # Deep Midnight Navy canvas
    "bg_card": "#161C36",          # Elevated dark card
    "bg_input": "#10162B",         # Recessed input fields
    "border": "#263056",           # Subtle navy divider
    "border_focus": "#7BB5EF",     # Bright cyan-blue focus ring
    
    # Typography
    "text_main": "#F8FAFC",        # Crisp white text (16.0:1)
    "text_muted": "#94A3B8",       # Slate-400 (Accessible secondary, 6.5:1)
    "text_disabled": "#475569",    # Slate-600
    
    # Brand Action Colors (Adapted for Dark Elevation)
    "primary": "#34D399",          # Mint Green CTA (High visibility in dark)
    "primary_hover": "#10B981",
    "primary_text": "#06281E",     # Deep Forest Dark text
    
    "secondary": "#7BB5EF",        # Sky Blue CTA
    "secondary_hover": "#5A9FE6",
    "secondary_text": "#08182D",   # Dark contrast text
    
    "accent": "#F6CE4C",           # Warm Gold
    "accent_hover": "#E5BC36",
    "accent_text": "#1E1805",
    
    "supporting": "#9B93EE",       # Soft Lavender
    "supporting_hover": "#857BE8",
    "supporting_text": "#131032",
    
    "danger": "#E66360",           # Coral Red
    "danger_hover": "#D14D4A",
    "danger_text": "#FFFFFF",
    "danger_inline": "#FCA5A5",    # Light coral for readable text in dark mode
    
    "success": "#34D399",          # Vibrant Mint
    "success_hover": "#10B981",
    "success_bg": "#064E3B",
    "success_text": "#6EE7B7",
    
    # Table & List Components
    "tree_bg": "#10162B",
    "tree_heading_bg": "#161C36",
    "tree_heading_fg": "#94A3B8",
    "tree_row_even": "#10162B",
    "tree_row_odd": "#141A33",
    "tree_row_select": "#222D52",
    "tree_row_select_fg": "#7BB5EF",
    
    # Status Row Tints (Dark Mode)
    "status_local_bg": "#064E3B",
    "status_local_fg": "#6EE7B7",
    "status_sync_bg": "#0C4A6E",
    "status_sync_fg": "#7BB5EF",
    "status_cloud_bg": "#1E293B",
    "status_cloud_fg": "#94A3B8",
    "status_notfound_bg": "#7F1D1D",
    "status_notfound_fg": "#FCA5A5",
}
```

---

## 4. Typography Scale & Font Architecture

`ui-ux-pro-max` নিয়ম অনুযায়ী **১২px / ৯.৫pt এর নিচে কোনো ফন্ট ব্যবহার করা নিষিদ্ধ (`Text < 12px body anti-pattern`)**। ৭pt ও ৮pt পুরোপুরি বাদ দিয়ে নিচের সুসংগত টাইপ স্কেল ব্যবহার করতে হবে:

| Role | Font Family | Size (pt) | Size (px) | Weight | Line Height | Usage Example |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Display** | `Segoe UI` | 15 pt | 20 px | Bold | 1.2 | Main Window Header Title |
| **Title** | `Segoe UI` | 13 pt | 17 px | Bold | 1.3 | Dialog Title, Modal Headers |
| **Subtitle** | `Segoe UI` | 11 pt | 15 px | SemiBold | 1.4 | Section Card Headers, Table Headings |
| **Body (Default)** | `Segoe UI` | 10.5 pt| 14 px | Regular | 1.5 | Primary Button Labels, Table Cell Values |
| **Caption / Meta** | `Segoe UI` | 9.5 pt | 12.5 px| Regular | 1.4 | Timestamps, Secondary Badges, Helper Text |
| **Code / Monospace**| `Consolas` | 10.5 pt| 14 px | Regular | 1.4 | Order IDs (`#456883`), File Paths, Logs |

```python
# ফন্ট হেল্পার ফাংশন (Unified Type Token Generator)
def get_font(role="body"):
    fonts = {
        "display":  ("Segoe UI", 15, "bold"),
        "title":    ("Segoe UI", 13, "bold"),
        "subtitle": ("Segoe UI", 11, "bold"),
        "body":     ("Segoe UI", 10.5),
        "button":   ("Segoe UI", 10.5, "bold"),
        "caption":  ("Segoe UI", 9.5),
        "code":     ("Consolas", 10.5)
    }
    return fonts.get(role, fonts["body"])
```

---

## 5. Spacing, Layout Rhythm & Geometry

### ৫.১ ৪/৮dp ইনক্রিমেন্টাল স্পেসিং স্কেল
এলোমেলো অযৌক্তিক প্যাডিং (যেমন ৩, ৫, ৭, ১৪, ১৮) বাদ দিয়ে স্ট্যান্ডার্ড ৪/৮dp গ্রিড প্রযোজ্য:

| Token | Dimension | Applied Use Cases |
| :--- | :--- | :--- |
| `space-1` | 4 px | মাইক্রো ইনসেট, আইকন ও টেক্সটের মাঝখানের ক্ষুদ্র স্পেস |
| `space-2` | 8 px | বাটন ইন্টারনাল প্যাডিং, ব্যাজ প্যাডিং, ইনপুট ও লেবেলের গ্যাপ |
| `space-3` | 12 px | কম্প্যাক্ট বাটন হরিজন্টাল প্যাডিং, কার্ড হেডার মার্জিন |
| `space-4` | 16 px | স্ট্যান্ডার্ড কন্টেইনার ইনসেট (`padx=16`), কার্ড ইন্টারনাল প্যাডিং |
| `space-6` | 24 px | প্রধান সেকশনের মাঝে ভার্টিক্যাল ব্যবধান |
| `space-8` | 32 px | উইন্ডো রুট ক্যানভাস মার্জিন, প্রধান কন্টেইনার ডিভাইডার |

### ৫.২ উইন্ডো জিওমেট্রি ও ডিসপ্লে স্কেলিং রুলস
- **সমস্যা সমাধান:** উইন্ডোজের ১০৮০p স্ক্রিনে ১৫০% ডিসপ্লে স্কেলিংয়ে যাতে কোনো উপাদান কেটে না যায়, তাই মিনিমাম সাইজ পরিবর্তন করা হলো:
  - **Previous (Broken):** `self.minsize(1160, 580)`
  - **Standardized:** `self.minsize(980, 560)` (১০৮০p @ ১৫০% স্কেলে ভার্চুয়াল উইডথ ১২৮০px-এ স্বাচ্ছন্দ্যে ফিট হয়)
- **Default Startup Geometry:** `1200 × 680 px` (উইন্ডোজ টাস্কবার ও টাইটেলবার রেখে সেন্টারে ওপেন হবে)।

### ৫.৩ ক্লিক টার্গেট সাইজ (Desktop Click Hit Areas)
- **Primary Buttons:** Minimum Height **32 px**, Horizontal Padding **16 px**.
- **Compact Toolbar / Action Buttons:** Minimum Height **28 px**, Minimum Width **28 px**.
- **Close / Clear ("✕") Buttons:** Minimum Hit Area **28 × 28 px** (পূর্বের অতি ক্ষুদ্র ২২×২২px বর্জন)।
- **Touch Spacing:** পাশাপাশি অবস্থিত বাটনগুলোর মধ্যে ন্যূনতম **8 px** ব্যবধান (`padx=(0, 8)`).

---

## 6. Iconography Standards (No Emoji Policy)

> [!IMPORTANT]
> **No Emoji as Structural Icons:**
> বাটনে, ন্যাভিগেশনে বা হেডারে কোনো অবস্থাতেই ইউনিকোড ইমোজি (যেমন 🚀, ✨, 🔔, 🧹, 🗑️, ⏹, ⏸) ব্যবহার করা যাবে না।

### ৬.১ আধুনিক ভেক্টর আইকন আর্কিটেকচার
ইমোজির বিকল্প হিসেবে ভেক্টর SVG/PNG আইকন লোড করে `customtkinter.CTkImage` দিয়ে ব্যবহার করতে হবে:

```python
# ভেক্টর আইকন লোডার প্যাটার্ন
def load_ui_icon(name, size=(16, 16)):
    """Loads a PNG vector icon and returns a themed CTkImage"""
    icon_path_light = os.path.join(ASSETS_DIR, "icons", "light", f"{name}.png")
    icon_path_dark = os.path.join(ASSETS_DIR, "icons", "dark", f"{name}.png")
    
    if os.path.exists(icon_path_light) and os.path.exists(icon_path_dark):
        return ctk.CTkImage(
            light_image=Image.open(icon_path_light),
            dark_image=Image.open(icon_path_dark),
            size=size
        )
    return None
```

### ৬.২ আইকন ও টেক্সট পেয়ারিং তালিকা
| পূর্বের ইমোজি | নতুন টেক্সট ও আইকন লেবেল | বাটন স্টাইল |
| :--- | :--- | :--- |
| `🚀 Update & Restart Now` | `Update & Restart Now` (Rocket Vector Icon) | Primary CTA (`#292194`) |
| `🧹 Clean Duplicate` | `Clean & Deduplicate` (Broom Vector Icon) | Supporting Secondary |
| `🗑 Clean Dash` | `Clear Dashboard` (Trash Vector Icon) | Outline Danger |
| `⏹ Stop` | `Stop Batch` (Square Vector Icon) | Solid Danger (`#E66360`) |
| `⏸ Pause` | `Pause Sync` (Pause Vector Icon) | Solid Accent (`#F6CE4C`) |
| `☁ Make Cloud` | `Free Up Space` (Cloud Vector Icon) | Secondary CTA (`#7BB5EF`) |
| `⚙ Settings` | `Settings` (Gear Vector Icon) | Ghost Toolbar Button |

---

## 7. Component & Widget Specifications

### ৭.১ ডায়ালগ আর্কিটেকচার (Unified `ctk.CTkToplevel`)
সকল সেকেন্ডারি উইন্ডো ও ডায়ালগ (`UpdateDialog`, `WhatsNewDialog`, `NotificationCenterDialog`, `LocalCleanDialog`, `OrderReviewDialog`, `HistoryTrackerDialog`, `SettingsDialog`) সরাসরি `ctk.CTkToplevel` থেকে ইনহেরিট করবে।
- **Never use `tk.Toplevel` with hardcoded dark backgrounds.**
- প্রতিটি ডায়ালগ সক্রিয় থিমের টোকেন গ্রহণ করবে এবং উইন্ডোজ ডার্ক/লাইট মোড পরিবর্তনের সাথে সাথে সমন্বয় করবে।

### ৭.২ নন-ব্লকিং টোস্ট নোটিফিকেশন (`messagebox` এর বিকল্প)
৫৮টি ব্লকিং পপআপের বদলে নন-ব্লকিং লাইভ স্ট্যাটাস পিল ব্যবহার করা হবে:
```python
def show_toast(self, message, level="info", duration_ms=3000):
    """Displays a clean, non-blocking animated status pill"""
    colors = {
        "info":    (self.theme["primary"], "#FFFFFF"),
        "success": (self.theme["success"], "#FFFFFF"),
        "warning": (self.theme["accent"], "#181825"),
        "danger":  (self.theme["danger"], "#FFFFFF")
    }
    bg, fg = colors.get(level, colors["info"])
    self.status_pill_lbl.configure(text=message, fg_color=bg, text_color=fg)
    self.after(duration_ms, lambda: self.status_pill_lbl.configure(
        text="Ready", fg_color="transparent", text_color=self.theme["text_muted"]
    ))
```

### ৭.৩ নিরাপদ ইভেন্ট বাইন্ডিং (Unbind Bug Fix)
ভেন্ডর পপআপ বন্ধ করার সময় কখনো পুরো অ্যাপ্লিকেশনের গ্লোবাল মাউস ইভেন্ট আনবাইন্ড করা যাবে না:
```python
# ❌ ক্ষতিকর অ্যান্টি-প্যাটার্ন:
# self.unbind_all("<Button-1>")

# ✅ নিরাপদ ও সঠিক প্যাটার্ন:
if hasattr(self, "_vendor_outside_click_id") and self._vendor_outside_click_id:
    self.unbind("<Button-1>", self._vendor_outside_click_id)
    self._vendor_outside_click_id = None
```

---

## 8. Pre-Delivery Checklist (QA Verification)

- [ ] **লোগো নিরাপত্তা:** `logo_header.png` ও `logo_64.png` বিকৃতিহীনভাবে অনুপাত বজায় রেখে দৃশ্যমান।
- [ ] **কালার কনট্রাস্ট:** সকল সাধারণ টেক্সটের কনট্রাস্ট রেশিও $\ge 4.5:1$ (Light এবং Dark উভয় মোডে)।
- [ ] **রাইট-ক্লিক মেনু:** Light মোডে কোনো সাদা টেক্সট সাদা ব্যাকগ্রাউন্ডে প্রদর্শিত হচ্ছে না।
- [ ] **টাইপোগ্রাফি:** কোডের কোথাও ৭pt বা ৮pt ফন্ট নেই; সর্বনিম্ন ফন্ট সাইজ ৯.৫pt (১২.৫px)।
- [ ] **ইমোজি বর্জন:** বাটনের মধ্যে কোনো ইউনিকোড ইমোজি নেই; প্রয়োজনে ভেক্টর আইকন ব্যবহৃত।
- [ ] **টুলকিট ঐক্য:** সকল ডায়ালগ `ctk.CTkToplevel` হিসেবে রেন্ডার হচ্ছে; কোনো `tk.Toplevel` হার্ডকোডেড ব্ল্যাক উইন্ডো নেই।
- [ ] **স্কেলিং ও স্ক্রিন সাইজ:** উইন্ডো মিনিমাম সাইজ `980x560` থাকায় ১০৮০p @ ১৫০% ডিসপ্লেতে কোনো অংশ কাটছে না।
- [ ] **ইভেন্ট স্থিতিশীলতা:** ভেন্ডর ড্রপডাউন বন্ধ করার পর অন্যান্য উইজেটের ক্লিক স্বাভাবিকভাবে কার্যকর থাকে।

