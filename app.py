import os
import sys
import json
import re
import subprocess
import threading
import ctypes
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
CURRENT_VERSION = "v1.3.0"
GITHUB_REPO = "bishojit-sarker/Smart-Dropbox-QC-Batch-Loader"

# Windows Cloud Filter Attributes
FILE_ATTRIBUTE_PINNED = 0x80000
FILE_ATTRIBUTE_UNPINNED = 0x100000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_history(hist):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, indent=2)
    except Exception:
        pass

def mark_order_history(order_id, vendor, folder_path, status, file_count=0):
    hist = load_history()
    key = f"{order_id}_{vendor}" if vendor and vendor != "-" else str(order_id)
    entry = hist.get(key, {})
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    entry.update({
        "order_id": str(order_id),
        "vendor": vendor,
        "path": folder_path,
        "status": status,  # "local" or "online"
        "files": file_count,
        "last_updated": now_str
    })
    if status == "local" and "downloaded_at" not in entry:
        entry["downloaded_at"] = now_str
    elif status == "online":
        entry["freed_at"] = now_str

    hist[key] = entry
    save_history(hist)

def get_tracked_local_orders():
    hist = load_history()
    local_orders = []
    for key, item in hist.items():
        if item.get("status") == "local":
            p = item.get("path")
            if p and os.path.isdir(p):
                local_orders.append(item)
    return local_orders

def is_folder_local_on_disk(folder_path):
    """
    Checks if a folder contains hydrated/pinned files taking physical space on disk.
    """
    if not os.path.isdir(folder_path):
        return False, 0
    kernel32 = ctypes.windll.kernel32 if hasattr(ctypes, "windll") else None
    if not kernel32:
        return False, 0

    has_local = False
    file_count = 0
    for root, _, files in os.walk(folder_path):
        for f in files:
            file_count += 1
            fp = os.path.join(root, f)
            try:
                attrs = kernel32.GetFileAttributesW(fp)
                if attrs != -1 and (attrs & FILE_ATTRIBUTE_PINNED):
                    has_local = True
                    break
            except Exception:
                pass
        if has_local:
            break
    return has_local, file_count

def cleanup_old_executable():
    try:
        old_exe = sys.executable + ".old"
        if os.path.exists(old_exe):
            os.remove(old_exe)
    except Exception:
        pass

def check_for_updates(parent=None, silent=True):
    def _worker():
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": "QC-Batch-Loader-Updater"}
            )
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            latest_tag = data.get("tag_name", "").strip()
            if not latest_tag or latest_tag == CURRENT_VERSION:
                if not silent and parent:
                    parent.after(0, lambda: messagebox.showinfo("Up to Date", f"You are using the latest version ({CURRENT_VERSION})!"))
                return

            download_url = None
            for asset in data.get("assets", []):
                if asset.get("name") == "QC_Batch_Loader.exe":
                    download_url = asset.get("browser_download_url")
                    break

            if not download_url:
                return

            def _prompt():
                body = data.get("body", "Bug fixes and performance improvements.")
                msg = (
                    f"A new version ({latest_tag}) is available!\n"
                    f"Your current version: {CURRENT_VERSION}\n\n"
                    f"What's New:\n{body[:300]}\n\n"
                    "Would you like to automatically update now?"
                )
                ans = messagebox.askyesno("Update Available", msg)
                if ans:
                    _perform_update(download_url, latest_tag, parent)

            if parent:
                parent.after(0, _prompt)
        except Exception as e:
            if not silent and parent:
                parent.after(0, lambda: messagebox.showerror("Update Check Failed", f"Could not check for updates:\n{e}"))

    threading.Thread(target=_worker, daemon=True).start()

def _perform_update(download_url, latest_tag, parent=None):
    try:
        cur_exe = sys.executable
        if not cur_exe.lower().endswith("qc_batch_loader.exe"):
            webbrowser.open(download_url)
            return

        old_exe = cur_exe + ".old"
        new_exe_tmp = cur_exe + ".tmp"

        if parent:
            parent.status_var.set(f"Downloading update {latest_tag} from GitHub...")

        urllib.request.urlretrieve(download_url, new_exe_tmp)

        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except Exception:
                pass

        os.rename(cur_exe, old_exe)
        os.rename(new_exe_tmp, cur_exe)

        messagebox.showinfo("Update Complete", f"Successfully updated to {latest_tag}! The application will now restart.")
        subprocess.Popen([cur_exe])
        os._exit(0)
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to complete automatic update:\n{e}")

def auto_detect_dropbox_path():
    """
    Automatically detects Dropbox root folder on ANY Windows computer without manual input.
    Checks Dropbox's official info.json (business & personal), userprofile directory, or fallback.
    """
    candidate_json_paths = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Dropbox", "info.json"),
        os.path.join(os.environ.get("APPDATA", ""), "Dropbox", "info.json"),
    ]
    for json_path in candidate_json_paths:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for account_type in ["business", "personal"]:
                    acc = data.get(account_type)
                    if isinstance(acc, dict):
                        # root_path is preferred for team/business (e.g. C:\Users\User\Path Dropbox)
                        if "root_path" in acc and os.path.isdir(acc["root_path"]):
                            return acc["root_path"]
                        if "path" in acc and os.path.isdir(acc["path"]):
                            return acc["path"]
            except Exception:
                pass

    # Search in current user's profile directory for any *Dropbox* folder
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    if os.path.isdir(user_profile):
        try:
            for entry in os.listdir(user_profile):
                full_p = os.path.join(user_profile, entry)
                if os.path.isdir(full_p) and "dropbox" in entry.lower():
                    return full_p
        except Exception:
            pass

    return os.path.join(user_profile, "Dropbox")

DEFAULT_DROPBOX_PATH = auto_detect_dropbox_path()

def load_config():
    detected_path = auto_detect_dropbox_path()
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                saved_path = cfg.get("dropbox_path")
                # If the saved path still exists on this specific computer, keep it
                if saved_path and os.path.isdir(saved_path):
                    return cfg
        except Exception:
            pass
    return {"dropbox_path": detected_path}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

class HistoryTrackerDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("📜 বকেয়া তালিকা ও হিস্ট্রি ট্র্যাকার — Persistent History Tracker")
        self.geometry("900x580")
        self.minsize(780, 480)
        self.configure(bg="#1e1e2e")
        self.transient(parent)
        self.grab_set()

        try:
            x = parent.winfo_x() + (parent.winfo_width() // 2) - 450
            y = parent.winfo_y() + (parent.winfo_height() // 2) - 290
            self.geometry(f"+{max(x, 50)}+{max(y, 50)}")
        except Exception:
            pass

        self.filter_var = tk.StringVar(value="pending")
        self._create_widgets()
        self._refresh_data()

    def _create_widgets(self):
        # 1. Top Header Frame
        top_frame = tk.Frame(self, bg="#1e1e2e")
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="📜 বকেয়া তালিকা ও হিস্ট্রি ট্র্যাকার (Persistent History)",
            font=("Segoe UI", 13, "bold"),
            bg="#1e1e2e",
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        subtitle_lbl = tk.Label(
            top_frame,
            text="যেসব অর্ডার আপনি নিজে লোকাল করে কাজ করেছেন, কেবল সেগুলোর সংরক্ষিত তালিকা ও ডিস্ক স্পেস রিলিজ",
            font=("Segoe UI", 8),
            bg="#1e1e2e",
            fg="#94a3b8"
        )
        subtitle_lbl.pack(side="left", padx=8, pady=(3, 0))

        close_btn = tk.Button(
            top_frame,
            text="✕ Close",
            command=self.destroy,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        close_btn.pack(side="right")

        # 2. Control Bar (Filter & Summary Stats)
        ctrl_card = tk.Frame(self, bg="#252538", bd=1, relief="solid")
        ctrl_card.pack(fill="x", padx=16, pady=4)

        # Filter Radios on Left
        filter_box = tk.Frame(ctrl_card, bg="#252538")
        filter_box.pack(side="left", padx=10, pady=6)

        tk.Label(filter_box, text="ফিল্টার:", bg="#252538", fg="#f8fafc", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 6))

        rb_pending = tk.Radiobutton(
            filter_box,
            text="🔴 শুধু বকেয়া অর্ডার (Pending Local)",
            variable=self.filter_var,
            value="pending",
            command=self._refresh_data,
            bg="#252538",
            fg="#f8fafc",
            activebackground="#252538",
            activeforeground="#60a5fa",
            selectcolor="#181825",
            font=("Segoe UI", 9, "bold")
        )
        rb_pending.pack(side="left", padx=4)

        rb_all = tk.Radiobutton(
            filter_box,
            text="📋 সমস্ত হিস্ট্রি (All History)",
            variable=self.filter_var,
            value="all",
            command=self._refresh_data,
            bg="#252538",
            fg="#94a3b8",
            activebackground="#252538",
            activeforeground="#60a5fa",
            selectcolor="#181825",
            font=("Segoe UI", 9)
        )
        rb_all.pack(side="left", padx=4)

        # Stats Label on Right
        self.stats_lbl = tk.Label(
            ctrl_card,
            text="বকেয়া: 0 টি   |   মুক্ত: 0 টি   |   মোট: 0 টি",
            bg="#252538",
            fg="#93c5fd",
            font=("Segoe UI", 9, "bold")
        )
        self.stats_lbl.pack(side="right", padx=12, pady=6)

        # 3. Table (Treeview)
        tree_frame = tk.Frame(self, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=16, pady=4)

        columns = ("order_id", "vendor", "status", "files", "time")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("status", text="Sync Status (ডিস্ক অবস্থা)")
        self.tree.heading("files", text="Files")
        self.tree.heading("time", text="ডাউনলোড / আপডেট সময়")

        self.tree.column("order_id", width=120, anchor="w")
        self.tree.column("vendor", width=140, anchor="w")
        self.tree.column("status", width=200, anchor="center")
        self.tree.column("files", width=70, anchor="center")
        self.tree.column("time", width=180, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        self.tree.tag_configure("pending_tag", foreground="#f87171")
        self.tree.tag_configure("online_tag", foreground="#34d399")

        self.tree.bind("<Double-1>", lambda e: self._open_selected_folder())

        # Context Menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#252538", fg="white", activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)
        self.context_menu.add_command(label="☁️ Make this Order Online-Only", command=self._free_selected)
        self.context_menu.add_command(label="📋 Load into Main QC Table", command=self._load_to_main_table)
        self.tree.bind("<Button-3>", self._on_tree_right_click)

        # 4. Action Buttons Bar at Bottom
        btn_bar = tk.Frame(self, bg="#1e1e2e")
        btn_bar.pack(fill="x", padx=16, pady=(6, 12))

        # Left Action Group
        left_btns = tk.Frame(btn_bar, bg="#1e1e2e")
        left_btns.pack(side="left")

        open_btn = tk.Button(
            left_btns,
            text="📂 Open Folder",
            command=self._open_selected_folder,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=10,
            pady=4
        )
        open_btn.pack(side="left", padx=(0, 6))

        load_btn = tk.Button(
            left_btns,
            text="📋 Load to QC Table",
            command=self._load_to_main_table,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            padx=10,
            pady=4
        )
        load_btn.pack(side="left", padx=(0, 6))

        clear_hist_btn = tk.Button(
            left_btns,
            text="🗑️ Clear Completed History",
            command=self._clear_online_history,
            bg="#252538",
            fg="#94a3b8",
            activebackground="#ef4444",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=4
        )
        clear_hist_btn.pack(side="left")

        # Right Action Group (Primary Cleanup Actions)
        right_btns = tk.Frame(btn_bar, bg="#1e1e2e")
        right_btns.pack(side="right")

        single_online_btn = tk.Button(
            right_btns,
            text="☁️ Make Selected Online",
            command=self._free_selected,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=5
        )
        single_online_btn.pack(side="left", padx=(0, 6))

        free_all_btn = tk.Button(
            right_btns,
            text="⚡ সব বকেয়া অনলাইন করুন (Make ALL Pending Online)",
            command=self._free_all_pending,
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=14,
            pady=5
        )
        free_all_btn.pack(side="left")

    def _on_tree_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _refresh_data(self):
        self.tree.delete(*self.tree.get_children())
        hist = load_history()
        filter_mode = self.filter_var.get()

        local_count = 0
        online_count = 0

        # Count and sync with existing paths
        updated = False
        for key, item in list(hist.items()):
            p = item.get("path")
            if item.get("status") == "local":
                if not p or not os.path.isdir(p):
                    item["status"] = "online"
                    hist[key] = item
                    updated = True

            if item.get("status") == "local":
                local_count += 1
            else:
                online_count += 1

        if updated:
            save_history(hist)

        self.stats_lbl.config(
            text=f"🔴 বকেয়া (Local): {local_count} টি   |   🟢 মুক্ত (Online): {online_count} টি   |   📁 মোট রেকর্ড: {len(hist)} টি"
        )

        sorted_keys = sorted(
            hist.keys(),
            key=lambda k: (
                0 if hist[k].get("status") == "local" else 1,
                hist[k].get("last_updated") or hist[k].get("downloaded_at") or ""
            ),
            reverse=False
        )

        for key in sorted_keys:
            entry = hist[key]
            status = entry.get("status", "online")

            if filter_mode == "pending" and status != "local":
                continue

            status_display = "🔴 বকেয়া (লোকাল মেমোরি দখল)" if status == "local" else "🟢 মুক্ত (Online-Only 0B)"
            tag = "pending_tag" if status == "local" else "online_tag"
            time_display = entry.get("downloaded_at") or entry.get("last_updated") or "-"
            files_display = str(entry.get("files", 0))

            self.tree.insert(
                "",
                "end",
                iid=key,
                values=(
                    f"#{entry.get('order_id', key)}",
                    entry.get("vendor", "-"),
                    status_display,
                    files_display,
                    time_display
                ),
                tags=(tag,)
            )

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_key = selected[0]
        hist = load_history()
        entry = hist.get(item_key)
        if entry and entry.get("path") and os.path.isdir(entry["path"]):
            try:
                os.startfile(entry["path"])
            except Exception as e:
                messagebox.showerror("এরর", f"ফোল্ডার খোলা যায়নি:\n{e}", parent=self)
        else:
            messagebox.showwarning("ফোল্ডার অনুপস্থিত", "ফোল্ডারটি পিসিতে পাওয়া যায়নি।", parent=self)

    def _free_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("অর্ডার নির্বাচন করুন", "দয়া করে তালিকা থেকে অন্তত একটি অর্ডার নির্বাচন করুন।", parent=self)
            return

        hist = load_history()
        count = 0
        for item_key in selected:
            entry = hist.get(item_key)
            if not entry:
                continue
            p = entry.get("path")
            if p and os.path.isdir(p):
                try:
                    cmd_files = f'attrib -P +U "{p}\\*.*" /s'
                    subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    cmd_folder = f'attrib -P +U "{p}" /d'
                    subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            mark_order_history(entry["order_id"], entry.get("vendor"), p, "online", entry.get("files", 0))
            count += 1

        self._refresh_data()
        self.parent._update_leftover_badge()
        messagebox.showinfo("অনলাইন সম্পন্ন", f"{count}টি অর্ডার সফলভাবে Online-Only করা হয়েছে!", parent=self)

    def _free_all_pending(self):
        tracked = get_tracked_local_orders()
        if not tracked:
            messagebox.showinfo("বকেয়া তালিকা", "🎉 চমৎকার! কোনো বকেয়া লোকাল অর্ডার নেই। আপনার হার্ডডিস্ক সম্পূর্ণ পরিষ্কার।", parent=self)
            return

        confirm = messagebox.askyesno(
            "সব বকেয়া অনলাইন করুন",
            f"আপনার মোট {len(tracked)}টি বকেয়া লোকাল অর্ডার রয়েছে।\n\n"
            f"আপনি কি কেবল আপনার কাজ করা এই {len(tracked)}টি অর্ডার Online-Only করে হার্ডড্রাইভ খালি করতে চান?\n\n"
            "(ড্রপবক্সের বাইরের কোনো অর্ডার এতে প্রভাবিত হবে না।)",
            parent=self
        )
        if not confirm:
            return

        self.parent._free_orders_in_background(tracked)
        self._refresh_data()
        self.parent._update_leftover_badge()
        messagebox.showinfo(
            "ডিস্ক স্পেস মুক্ত",
            f"সফলভাবে আপনার {len(tracked)}টি বকেয়া অর্ডার Online-Only করা হয়েছে!\nহার্ডডিস্কের জায়গা খালি হয়েছে।",
            parent=self
        )

    def _load_to_main_table(self):
        selected = self.tree.selection()
        hist = load_history()
        orders_to_load = []

        if selected:
            for s in selected:
                if s in hist:
                    orders_to_load.append(hist[s])
        else:
            for iid in self.tree.get_children():
                if iid in hist:
                    orders_to_load.append(hist[iid])

        if not orders_to_load:
            messagebox.showinfo("তথ্য", "লোড করার মতো কোনো অর্ডার নেই।", parent=self)
            return

        unique_ids = list(dict.fromkeys([it["order_id"] for it in orders_to_load]))
        formatted = "\n".join([f"#{oid}" for oid in unique_ids])
        self.parent.input_text.delete("1.0", "end")
        self.parent.input_text.insert("1.0", formatted)
        self.parent._update_order_count()
        self.parent.status_var.set(f"বকেয়া তালিকা থেকে {len(unique_ids)}টি অর্ডার কিউসি বক্সে লোড করা হয়েছে।")
        messagebox.showinfo("সফল", f"{len(unique_ids)}টি অর্ডার আইডি মূল কিউসি উইন্ডোতে লোড করা হয়েছে!", parent=self)
        self.destroy()

    def _clear_online_history(self):
        hist = load_history()
        cleaned_hist = {k: v for k, v in hist.items() if v.get("status") == "local"}
        cleared_count = len(hist) - len(cleaned_hist)
        if cleared_count == 0:
            messagebox.showinfo("হিস্ট্রি", "মুছে ফেলার মতো কোনো পুরনো অনলাইন হিস্ট্রি নেই।", parent=self)
            return

        confirm = messagebox.askyesno(
            "অনলাইন হিস্ট্রি ক্লিয়ার",
            f"{cleared_count}টি সম্পন্ন হওয়া (Online) অর্ডারের হিস্ট্রি মুছে ফেলতে চান?\n\n"
            "(বকেয়া থাকা লোকাল অর্ডারগুলো সুরক্ষিত থাকবে।)",
            parent=self
        )
        if confirm:
            save_history(cleaned_hist)
            self._refresh_data()
            self.parent._update_leftover_badge()
            messagebox.showinfo("সম্পন্ন", f"{cleared_count}টি সম্পন্ন হিস্ট্রি মুছে ফেলা হয়েছে।", parent=self)

class QCBatchLoaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"⚡ Smart Dropbox QC Batch Loader {CURRENT_VERSION}")
        self.geometry("900x750")
        self.minsize(780, 600)

        self.config_data = load_config()

        # Threading & Process Control state
        self.is_running = False
        self.is_paused = False
        self.stop_requested = False
        self.pause_event = threading.Event()
        self.pause_event.set()  # Not paused by default

        # Stores lookup details: {row_key: {"order_id": ..., "vendor": ..., "path": ..., "status": ..., "files": ...}}
        self.resolved_orders = {}

        self._setup_style()
        self._create_widgets()
        self._update_order_count()
        self._update_leftover_badge()

        # Check for updates in background 2.5s after launch
        self.after(2500, lambda: check_for_updates(self, silent=True))

    def _setup_style(self):
        self.configure(bg="#1e1e2e")
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Color Palette
        self.bg_color = "#1e1e2e"
        self.card_bg = "#252538"
        self.card_border = "#3a3a54"
        self.accent_blue = "#3b82f6"
        self.accent_green = "#10b981"
        self.accent_orange = "#f59e0b"
        self.accent_red = "#ef4444"
        self.text_main = "#f8fafc"
        self.text_muted = "#94a3b8"

        self.style.configure(".", background=self.bg_color, foreground=self.text_main, font=("Segoe UI", 9))
        self.style.configure("Card.TFrame", background=self.card_bg)
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_main)
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_main)
        self.style.configure("Muted.TLabel", background=self.card_bg, foreground=self.text_muted)
        
        self.style.configure("Total.Horizontal.TProgressbar", thickness=10, background="#10b981", troughcolor="#181825")
        self.style.configure("Single.Horizontal.TProgressbar", thickness=8, background="#3b82f6", troughcolor="#181825")
        
        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#181825",
            foreground=self.text_main,
            fieldbackground="#181825",
            rowheight=26,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#2b2b40",
            foreground=self.text_main,
            font=("Segoe UI", 9, "bold")
        )
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

    def _create_widgets(self):
        # 1. Top Header
        top_frame = tk.Frame(self, bg=self.bg_color)
        top_frame.pack(fill="x", padx=16, pady=(12, 6))

        title_lbl = tk.Label(
            top_frame,
            text="⚡ Smart Dropbox QC Batch Loader",
            font=("Segoe UI", 15, "bold"),
            bg=self.bg_color,
            fg="#60a5fa"
        )
        title_lbl.pack(side="left")

        version_badge = tk.Label(
            top_frame,
            text=CURRENT_VERSION,
            font=("Segoe UI", 8, "bold"),
            bg="#3b82f6",
            fg="white",
            padx=6,
            pady=1
        )
        version_badge.pack(side="left", padx=8, pady=(4, 0))

        subtitle_lbl = tk.Label(
            top_frame,
            text="Automated Multi-Vendor Offline Sync & Space Cleaner",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        subtitle_lbl.pack(side="left", padx=6, pady=(4, 0))

        update_btn = tk.Button(
            top_frame,
            text="🔄 Check Updates",
            command=lambda: check_for_updates(self, silent=False),
            bg="#252538",
            fg="#93c5fd",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=8,
            pady=2
        )
        update_btn.pack(side="right")

        self.leftover_btn = tk.Button(
            top_frame,
            text="📜 বকেয়া তালিকা: ০ (Drive Clean)",
            command=self._open_history_tracker,
            bg="#252538",
            fg="#10b981",
            activebackground="#3b82f6",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10,
            pady=2
        )
        self.leftover_btn.pack(side="right", padx=(0, 6))

        # 2. Dropbox Path Bar
        path_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        path_card.pack(fill="x", padx=16, pady=4)

        path_lbl = tk.Label(path_card, text="📁 Dropbox Root:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold"))
        path_lbl.pack(side="left", padx=(10, 6), pady=6)

        self.path_var = tk.StringVar(value=self.config_data.get("dropbox_path") or DEFAULT_DROPBOX_PATH)
        path_entry = tk.Entry(
            path_card,
            textvariable=self.path_var,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Segoe UI", 9)
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=4, pady=6, ipady=3)

        browse_btn = tk.Button(
            path_card,
            text="Browse...",
            command=self._browse_dropbox_path,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=10
        )
        browse_btn.pack(side="right", padx=10, pady=6)

        # 3. Main Split Panes (Input on Left, Table on Right)
        paned = tk.PanedWindow(self, orient="horizontal", bg=self.bg_color, bd=0, sashwidth=4)
        paned.pack(fill="both", expand=True, padx=16, pady=6)

        # Left Pane: Order ID Input
        left_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(left_frame, minsize=270, width=290)

        left_header = tk.Frame(left_frame, bg=self.card_bg)
        left_header.pack(fill="x", padx=10, pady=(8, 4))

        tk.Label(left_header, text="📋 Paste Order IDs:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold")).pack(side="left")
        self.count_lbl = tk.Label(left_header, text="0 orders", bg=self.card_bg, fg=self.text_muted, font=("Segoe UI", 8))
        self.count_lbl.pack(side="right")

        self.input_text = tk.Text(
            left_frame,
            bg="#181825",
            fg="#f8fafc",
            insertbackground="#ffffff",
            relief="flat",
            font=("Consolas", 10),
            wrap="word",
            padx=8,
            pady=8
        )
        self.input_text.pack(fill="both", expand=True, padx=10, pady=4)
        self.input_text.bind("<KeyRelease>", lambda e: self._update_order_count())

        # Buttons below text input
        btn_row_left = tk.Frame(left_frame, bg=self.card_bg)
        btn_row_left.pack(fill="x", padx=10, pady=(4, 8))

        clear_btn = tk.Button(
            btn_row_left,
            text="Clear",
            command=self._clear_input,
            bg="#374151",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        )
        clear_btn.pack(side="left", padx=(0, 4))

        paste_btn = tk.Button(
            btn_row_left,
            text="Paste",
            command=self._paste_clipboard,
            bg="#4b5563",
            fg="white",
            relief="flat",
            font=("Segoe UI", 8),
            cursor="hand2",
            padx=6,
            pady=2
        )
        paste_btn.pack(side="left", padx=(0, 4))

        dedup_btn = tk.Button(
            btn_row_left,
            text="🧹 Clean & Deduplicate",
            command=self._clean_and_deduplicate,
            bg="#6366f1",
            fg="white",
            activebackground="#4f46e5",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=6,
            pady=2
        )
        dedup_btn.pack(side="right")

        # Right Pane: Order Status Table
        right_frame = tk.Frame(paned, bg=self.card_bg, bd=1, relief="solid")
        paned.add(right_frame, minsize=460)

        right_header = tk.Frame(right_frame, bg=self.card_bg)
        right_header.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(right_header, text="📊 Orders & Sync Status:", bg=self.card_bg, fg=self.text_main, font=("Segoe UI", 9, "bold")).pack(side="left")

        open_btn = tk.Button(
            right_header,
            text="📂 Open Folder",
            command=self._open_selected_folder,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        open_btn.pack(side="right", padx=(4, 0))

        free_single_btn = tk.Button(
            right_header,
            text="☁️ Make Selected Online",
            command=self._make_selected_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        free_single_btn.pack(side="right")

        tree_frame = tk.Frame(right_frame, bg="#181825")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=4)

        columns = ("order_id", "vendor", "status", "files")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("vendor", text="Vendor")
        self.tree.heading("status", text="Sync Status")
        self.tree.heading("files", text="Files")

        self.tree.column("order_id", width=110, anchor="w")
        self.tree.column("vendor", width=140, anchor="w")
        self.tree.column("status", width=150, anchor="center")
        self.tree.column("files", width=70, anchor="center")

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<Button-3>", self._on_tree_right_click)

        # Context menu for right-click on table rows
        self.context_menu = tk.Menu(self, tearoff=0, bg="#252538", fg="white", activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(label="📂 Open in File Explorer", command=self._open_selected_folder)
        self.context_menu.add_command(label="☁️ Make this Order Online-Only", command=self._make_selected_online)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📥 Re-download (Make Local)", command=self._make_selected_local)

        # 4. Action Buttons & Controls Card
        action_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        action_card.pack(fill="x", padx=16, pady=6)

        btn_container = tk.Frame(action_card, bg=self.card_bg)
        btn_container.pack(fill="x", padx=12, pady=8)

        # Make Local Button
        self.btn_make_local = tk.Button(
            btn_container,
            text="📥 1. Make Local (Ready for QC)",
            command=self._start_make_local,
            bg=self.accent_green,
            fg="white",
            activebackground="#059669",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_make_local.pack(side="left", fill="x", expand=True, padx=(0, 4))

        # Free Up Space Button
        self.btn_make_online = tk.Button(
            btn_container,
            text="☁️ 2. Free Up Space (Make Online-Only)",
            command=self._start_make_online,
            bg="#0284c7",
            fg="white",
            activebackground="#0369a1",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_make_online.pack(side="left", fill="x", expand=True, padx=(4, 8))

        # Pause / Resume Button
        self.btn_pause = tk.Button(
            btn_container,
            text="⏸️ Pause",
            command=self._toggle_pause,
            state="disabled",
            bg=self.accent_orange,
            fg="white",
            activebackground="#d97706",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_pause.pack(side="left", padx=(0, 4))

        # Stop Button
        self.btn_stop = tk.Button(
            btn_container,
            text="⏹️ Stop",
            command=self._request_stop,
            state="disabled",
            bg=self.accent_red,
            fg="white",
            activebackground="#dc2626",
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            padx=12,
            pady=7
        )
        self.btn_stop.pack(side="left")

        # 5. Dual Progress Indicators Card (Total & Single Order)
        progress_card = tk.Frame(self, bg=self.card_bg, bd=1, relief="solid")
        progress_card.pack(fill="x", padx=16, pady=4)

        # Total Progress Row
        total_p_row = tk.Frame(progress_card, bg=self.card_bg)
        total_p_row.pack(fill="x", padx=12, pady=(6, 2))

        self.total_lbl = tk.Label(
            total_p_row,
            text="Total Progress: 0% (0 / 0 Orders)",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_bg,
            fg=self.text_main
        )
        self.total_lbl.pack(side="left")

        self.total_progress = ttk.Progressbar(progress_card, style="Total.Horizontal.TProgressbar", mode="determinate")
        self.total_progress.pack(fill="x", padx=12, pady=(0, 4))

        # Single Order Progress Row
        single_p_row = tk.Frame(progress_card, bg=self.card_bg)
        single_p_row.pack(fill="x", padx=12, pady=(2, 2))

        self.single_lbl = tk.Label(
            single_p_row,
            text="Single Order: 0% (0 / 0 Files)",
            font=("Segoe UI", 8),
            bg=self.card_bg,
            fg=self.text_muted
        )
        self.single_lbl.pack(side="left")

        self.single_progress = ttk.Progressbar(progress_card, style="Single.Horizontal.TProgressbar", mode="determinate")
        self.single_progress.pack(fill="x", padx=12, pady=(0, 6))

        # 6. Bottom Status Bar & Log
        bottom_frame = tk.Frame(self, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=16, pady=(2, 8))

        self.status_var = tk.StringVar(value="Ready. Paste Order IDs and choose an action.")
        status_lbl = tk.Label(
            bottom_frame,
            textvariable=self.status_var,
            bg=self.bg_color,
            fg="#93c5fd",
            font=("Segoe UI", 9)
        )
        status_lbl.pack(side="left")

    def _browse_dropbox_path(self):
        chosen = filedialog.askdirectory(initialdir=self.path_var.get(), title="Select Dropbox Root Folder")
        if chosen:
            self.path_var.set(chosen)
            self.config_data["dropbox_path"] = chosen
            save_config(self.config_data)

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        self._update_order_count()

    def _paste_clipboard(self):
        try:
            clip = self.clipboard_get()
            self.input_text.insert("end", clip)
            self._update_order_count()
        except Exception:
            pass

    def _parse_order_ids(self):
        raw = self.input_text.get("1.0", "end")
        tokens = re.split(r"[\r\n,;\t\s]+", raw)
        cleaned = []
        raw_non_empty = 0
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            raw_non_empty += 1
            # 1. Remove leading hash: e.g. '#456883-P1' -> '456883-P1'
            t_clean = re.sub(r"^#\s*", "", t)
            # 2. Strip any suffixes after dash or underscore: e.g. '456883-P1' -> '456883'
            t_clean = re.split(r"[-_]", t_clean)[0].strip()
            if t_clean and t_clean not in cleaned:
                cleaned.append(t_clean)
        return cleaned, raw_non_empty

    def _update_order_count(self):
        unique_orders, total_lines = self._parse_order_ids()
        self.count_lbl.config(text=f"Total: {total_lines} lines | Unique: {len(unique_orders)}")

    def _clean_and_deduplicate(self):
        unique_orders, total_lines = self._parse_order_ids()
        if not unique_orders:
            messagebox.showinfo("Deduplicate", "No Order IDs found to clean.")
            return

        formatted = "\n".join([f"#{oid}" for oid in unique_orders])
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", formatted)
        self._update_order_count()
        self.status_var.set(f"Deduplicated! {total_lines} lines cleaned into {len(unique_orders)} unique orders.")

    def _find_all_vendor_matches(self, base_path, order_id):
        """
        Scans ALL vendors in base_path for order_id or #order_id.
        Returns a list of dicts:
        [
            {"vendor": ..., "path": ..., "files": [file1, file2...], "file_count": int}
        ]
        """
        matches = []
        if not os.path.isdir(base_path):
            return matches

        try:
            vendors = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        except Exception:
            return matches

        for vendor in vendors:
            v_dir = os.path.join(base_path, vendor)
            for prefix in ["#", "", "# "]:
                order_cand = os.path.join(v_dir, f"{prefix}{order_id}")
                if os.path.isdir(order_cand):
                    # Check for Completed / Complete folder
                    completed_dir = None
                    for sub in ["Completed", "Complete", "completed", "complete"]:
                        c_sub = os.path.join(order_cand, sub)
                        if os.path.isdir(c_sub):
                            completed_dir = c_sub
                            break

                    target_dir = completed_dir if completed_dir else order_cand
                    
                    # Collect all files recursively
                    files = []
                    for root, _, fs in os.walk(target_dir):
                        for f in fs:
                            files.append(os.path.join(root, f))

                    matches.append({
                        "vendor": vendor,
                        "path": target_dir,
                        "files": files,
                        "file_count": len(files)
                    })
                    break  # Break prefix loop for this vendor
        return matches

    def _on_tree_double_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self._open_selected_folder()

    def _open_selected_folder(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item = self.tree.item(selected[0])
        item_id = selected[0]
        
        info = self.resolved_orders.get(item_id)
        if not info:
            # Fallback by order_id string
            raw_id = str(item["values"][0]).strip()
            clean_id = re.sub(r"^#\s*", "", raw_id)
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if info and info.get("path") and os.path.isdir(info["path"]):
            try:
                os.startfile(info["path"])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open folder:\n{e}")
        else:
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")

    def _on_tree_right_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def _make_selected_online(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item_id = selected[0]
        item = self.tree.item(item_id)
        info = self.resolved_orders.get(item_id)
        if not info:
            raw_id = str(item["values"][0]).strip()
            clean_id = re.sub(r"^#\s*", "", raw_id)
            clean_id = re.split(r"[-_]", clean_id)[0].strip()
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")
            return

        folder_path = info["path"]
        order_id = info.get("order_id", item["values"][0])
        vendor = info.get("vendor", item["values"][1])
        file_count = info.get("files", item["values"][3])

        try:
            # Unpin files and folder: attrib -P +U
            cmd_files = f'attrib -P +U "{folder_path}\\*.*" /s'
            subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmd_folder = f'attrib -P +U "{folder_path}" /d'
            subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            status_text = "☁️ Online-Only"
            self.tree.item(item_id, values=(f"#{order_id}", vendor, status_text, str(file_count)))
            info["status"] = status_text
            mark_order_history(order_id, vendor, folder_path, "online", file_count)
            self._update_leftover_badge()
            self.status_var.set(f"☁️ Order #{order_id} ({vendor}) is now Online-Only. Disk space freed!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to free space:\n{e}")

    def _make_selected_local(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Order", "Please select an order from the list first.")
            return

        item_id = selected[0]
        item = self.tree.item(item_id)
        info = self.resolved_orders.get(item_id)
        if not info:
            raw_id = str(item["values"][0]).strip()
            clean_id = re.sub(r"^#\s*", "", raw_id)
            clean_id = re.split(r"[-_]", clean_id)[0].strip()
            info = self.resolved_orders.get(clean_id) or self.resolved_orders.get(f"#{clean_id}")

        if not info or not info.get("path") or not os.path.isdir(info["path"]):
            order_name = item["values"][0] if item.get("values") else "selected"
            messagebox.showwarning("Not Found", f"Folder path for order {order_name} is not available on disk.")
            return

        folder_path = info["path"]
        order_id = info.get("order_id", item["values"][0])
        vendor = info.get("vendor", item["values"][1])
        file_count = info.get("files", item["values"][3])

        try:
            cmd_files = f'attrib +P -U "{folder_path}\\*.*" /s'
            subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cmd_folder = f'attrib +P -U "{folder_path}" /d'
            subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            for root, _, files in os.walk(folder_path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        with open(fp, "rb") as fh:
                            fh.read(1024)
                    except Exception:
                        pass

            status_text = "✅ Local (Ready)"
            self.tree.item(item_id, values=(f"#{order_id}", vendor, status_text, str(file_count)))
            info["status"] = status_text
            mark_order_history(order_id, vendor, folder_path, "local", file_count)
            self._update_leftover_badge()
            self.status_var.set(f"✅ Order #{order_id} ({vendor}) is now Local and ready for QC.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to make local:\n{e}")

    def _update_leftover_badge(self):
        try:
            tracked = get_tracked_local_orders()
            count = len(tracked)
            if hasattr(self, "leftover_btn"):
                if count > 0:
                    self.leftover_btn.config(
                        text=f"⚠️ বকেয়া তালিকা: {count} টি লোকাল",
                        bg="#f59e0b",
                        fg="#111827",
                        activebackground="#d97706",
                        activeforeground="#ffffff"
                    )
                else:
                    self.leftover_btn.config(
                        text="📜 বকেয়া তালিকা: ০ (Drive Clean)",
                        bg="#252538",
                        fg="#10b981",
                        activebackground="#3b82f6",
                        activeforeground="#ffffff"
                    )
        except Exception:
            pass

    def _open_history_tracker(self):
        HistoryTrackerDialog(self)

    def _show_tracked_leftovers(self):
        self._open_history_tracker()

    def _free_orders_in_background(self, order_items):
        for it in order_items:
            folder_path = it.get("path")
            oid = it.get("order_id")
            vendor = it.get("vendor", "-")
            files = it.get("files", 0)
            if folder_path and os.path.isdir(folder_path):
                try:
                    cmd_files = f'attrib -P +U "{folder_path}\\*.*" /s'
                    subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    cmd_folder = f'attrib -P +U "{folder_path}" /d'
                    subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
            mark_order_history(oid, vendor, folder_path, "online", files)
        self._update_leftover_badge()

    def _set_controls_running(self, running):
        self.is_running = running
        self.is_paused = False
        self.stop_requested = False
        self.pause_event.set()

        state_actions = "disabled" if running else "normal"
        state_controls = "normal" if running else "disabled"

        self.btn_make_local.config(state=state_actions)
        self.btn_make_online.config(state=state_actions)
        if hasattr(self, "leftover_btn"):
            self.leftover_btn.config(state=state_actions)
        self.btn_pause.config(state=state_controls, text="⏸️ Pause", bg=self.accent_orange)
        self.btn_stop.config(state=state_controls)

    def _toggle_pause(self):
        if not self.is_running:
            return

        if self.is_paused:
            self.is_paused = False
            self.pause_event.set()
            self.btn_pause.config(text="⏸️ Pause", bg=self.accent_orange)
            self.status_var.set("Resumed processing...")
        else:
            self.is_paused = True
            self.pause_event.clear()
            self.btn_pause.config(text="▶️ Resume", bg=self.accent_green)
            self.status_var.set("⏸️ Paused by user. Click Resume to continue.")

    def _request_stop(self):
        if not self.is_running:
            return

        confirm = messagebox.askyesno("Stop Process", "Are you sure you want to stop the current batch?")
        if confirm:
            self.stop_requested = True
            self.pause_event.set()  # Unpause to let thread exit cleanly
            self.status_var.set("Stopping process, please wait...")

    def _start_make_local(self):
        if self.is_running:
            return
        orders, _ = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.")
            return

        # Storage Shield: Auto-Prompt Guard (strictly for user's previous orders)
        tracked_local = get_tracked_local_orders()
        prev_local = [it for it in tracked_local if it.get("order_id") not in orders]

        if prev_local:
            count = len(prev_local)
            sample_ids = ", ".join([f"#{it.get('order_id')}" for it in prev_local[:5]])
            if count > 5:
                sample_ids += f" and {count - 5} more"

            msg = (
                f"⚠️ Storage Guard Alert:\n\n"
                f"You have {count} order(s) that you previously worked on still saved locally on disk:\n"
                f"({sample_ids})\n\n"
                "Would you like to make ONLY your previous orders Online-Only now to free up disk space?\n\n"
                "• Click [Yes] to free your previous orders and proceed with new batch.\n"
                "• Click [No] to keep them local and proceed.\n"
                "• Click [Cancel] to abort.\n\n"
                "(No other orders on Dropbox will be touched)."
            )
            ans = messagebox.askyesnocancel("Storage Guard", msg)
            if ans is None:
                return
            if ans is True:
                self.status_var.set(f"Freeing {count} previous local orders...")
                self._free_orders_in_background(prev_local)

        self._set_controls_running(True)
        threading.Thread(target=self._process_make_local, args=(orders,), daemon=True).start()

    def _process_make_local(self, orders):
        base_path = self.path_var.get()
        total_orders = len(orders)

        self.total_progress["maximum"] = total_orders
        self.total_progress["value"] = 0
        self.single_progress["maximum"] = 100
        self.single_progress["value"] = 0

        self.tree.delete(*self.tree.get_children())
        self.resolved_orders = {}

        success_count = 0
        not_found_count = 0

        for i, order_id in enumerate(orders):
            if self.stop_requested:
                break
            self.pause_event.wait()
            if self.stop_requested:
                break

            # Update Total Progress
            pct = int((i / total_orders) * 100)
            self.total_lbl.config(text=f"Total Progress: {pct}% ({i} / {total_orders} Orders)")
            self.total_progress["value"] = i
            self.status_var.set(f"Searching vendors for #{order_id} ({i+1}/{total_orders})...")

            matches = self._find_all_vendor_matches(base_path, order_id)

            if not matches:
                status_text = "❌ Not Found"
                item_key = f"{order_id}_notfound"
                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0}
                self.resolved_orders[order_id] = self.resolved_orders[item_key]
                self.tree.insert("", "end", iid=item_key, values=(f"#{order_id}", "-", status_text, "0"))
                not_found_count += 1
            else:
                for match in matches:
                    if self.stop_requested:
                        break
                    self.pause_event.wait()
                    if self.stop_requested:
                        break

                    vendor = match["vendor"]
                    folder_path = match["path"]
                    file_list = match["files"]
                    total_files = len(file_list)

                    item_key = f"{order_id}_{vendor}"
                    item_id = self.tree.insert("", "end", iid=item_key, values=(f"#{order_id}", vendor, "⏳ Syncing...", str(total_files)))
                    self.tree.see(item_id)

                    try:
                        # 1. Windows Pin attributes on folder & files
                        cmd_files = f'attrib +P -U "{folder_path}\\*.*" /s'
                        subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        cmd_folder = f'attrib +P -U "{folder_path}" /d'
                        subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        # 2. Trigger instant hydration with Single Order Progress
                        self.single_progress["maximum"] = max(total_files, 1)
                        for f_idx, fp in enumerate(file_list):
                            if self.stop_requested:
                                break
                            self.pause_event.wait()
                            if self.stop_requested:
                                break

                            fname = os.path.basename(fp)
                            s_pct = int(((f_idx + 1) / max(total_files, 1)) * 100)
                            self.single_lbl.config(text=f"Current Order: #{order_id} ({vendor}) - {s_pct}% ({f_idx + 1}/{total_files} files)")
                            self.single_progress["value"] = f_idx + 1
                            self.status_var.set(f"Hydrating: {fname}...")

                            try:
                                with open(fp, "rb") as fh:
                                    fh.read(1024)
                            except Exception:
                                pass

                        status_text = "✅ Local (Ready)"
                        success_count += 1
                        mark_order_history(order_id, vendor, folder_path, "local", total_files)
                    except Exception as e:
                        status_text = f"⚠️ Error: {str(e)[:15]}"

                    self.tree.item(item_key, values=(f"#{order_id}", vendor, status_text, str(total_files)))
                    order_info = {
                        "order_id": order_id,
                        "vendor": vendor,
                        "path": folder_path,
                        "status": status_text,
                        "files": total_files
                    }
                    self.resolved_orders[item_key] = order_info
                    self.resolved_orders[order_id] = order_info
                    self.resolved_orders[f"#{order_id}"] = order_info

        # Completion or Stop state
        if self.stop_requested:
            self.status_var.set("⏹️ Process stopped by user.")
            messagebox.showwarning("Stopped", "Process was stopped by user.")
        else:
            self.total_lbl.config(text=f"Total Progress: 100% ({total_orders} / {total_orders} Orders)")
            self.total_progress["value"] = total_orders
            self.single_lbl.config(text="Single Order: 100% Complete")
            self.single_progress["value"] = 100
            self.status_var.set(f"Done! {success_count} folders ready locally, {not_found_count} not found.")
            messagebox.showinfo(
                "Batch Complete",
                f"Successfully prepared {success_count} vendor folders locally for QC!\n\n"
                f"Not found: {not_found_count} orders."
            )

        self._set_controls_running(False)
        self.after(0, self._update_leftover_badge)

    def _start_make_online(self):
        if self.is_running:
            return
        orders, _ = self._parse_order_ids()
        if not orders:
            messagebox.showwarning("No Orders", "Please paste or enter at least one Order ID.")
            return

        confirm = messagebox.askyesno(
            "Free Up Space",
            f"Are you sure you want to make {len(orders)} orders Online-Only?\n"
            "This will revert the files to 0-byte cloud placeholders and free up disk space."
        )
        if not confirm:
            return

        self._set_controls_running(True)
        threading.Thread(target=self._process_make_online, args=(orders,), daemon=True).start()

    def _process_make_online(self, orders):
        base_path = self.path_var.get()
        total_orders = len(orders)

        self.total_progress["maximum"] = total_orders
        self.total_progress["value"] = 0
        self.single_progress["maximum"] = 100
        self.single_progress["value"] = 0

        self.tree.delete(*self.tree.get_children())
        self.resolved_orders = {}

        freed_count = 0
        not_found_count = 0

        for i, order_id in enumerate(orders):
            if self.stop_requested:
                break
            self.pause_event.wait()
            if self.stop_requested:
                break

            pct = int((i / total_orders) * 100)
            self.total_lbl.config(text=f"Total Progress: {pct}% ({i} / {total_orders} Orders)")
            self.total_progress["value"] = i
            self.status_var.set(f"Freeing space for #{order_id} ({i+1}/{total_orders})...")

            matches = self._find_all_vendor_matches(base_path, order_id)

            if not matches:
                status_text = "❌ Not Found"
                item_key = f"{order_id}_notfound"
                self.resolved_orders[item_key] = {"order_id": order_id, "vendor": "-", "path": None, "status": status_text, "files": 0}
                self.resolved_orders[order_id] = self.resolved_orders[item_key]
                self.tree.insert("", "end", iid=item_key, values=(f"#{order_id}", "-", status_text, "0"))
                not_found_count += 1
            else:
                for match in matches:
                    if self.stop_requested:
                        break
                    self.pause_event.wait()
                    if self.stop_requested:
                        break

                    vendor = match["vendor"]
                    folder_path = match["path"]
                    total_files = match["file_count"]

                    item_key = f"{order_id}_{vendor}"
                    item_id = self.tree.insert("", "end", iid=item_key, values=(f"#{order_id}", vendor, "⏳ Freeing...", str(total_files)))
                    self.tree.see(item_id)

                    try:
                        # Mark files and folder as Unpinned: attrib -P +U
                        cmd_files = f'attrib -P +U "{folder_path}\\*.*" /s'
                        subprocess.run(cmd_files, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        cmd_folder = f'attrib -P +U "{folder_path}" /d'
                        subprocess.run(cmd_folder, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                        self.single_lbl.config(text=f"Current Order: #{order_id} ({vendor}) - 100% Space Freed")
                        self.single_progress["value"] = 100

                        status_text = "☁️ Online-Only"
                        freed_count += 1
                        mark_order_history(order_id, vendor, folder_path, "online", total_files)
                    except Exception as e:
                        status_text = f"⚠️ Error: {str(e)[:15]}"

                    self.tree.item(item_key, values=(f"#{order_id}", vendor, status_text, str(total_files)))
                    order_info = {
                        "order_id": order_id,
                        "vendor": vendor,
                        "path": folder_path,
                        "status": status_text,
                        "files": total_files
                    }
                    self.resolved_orders[item_key] = order_info
                    self.resolved_orders[order_id] = order_info
                    self.resolved_orders[f"#{order_id}"] = order_info

        if self.stop_requested:
            self.status_var.set("⏹️ Process stopped by user.")
            messagebox.showwarning("Stopped", "Process was stopped by user.")
        else:
            self.total_lbl.config(text=f"Total Progress: 100% ({total_orders} / {total_orders} Orders)")
            self.total_progress["value"] = total_orders
            self.single_lbl.config(text="Single Order: 100% Freed")
            self.single_progress["value"] = 100
            self.status_var.set(f"Done! {freed_count} folders reverted to Online-Only. Disk space recovered!")
            messagebox.showinfo(
                "Space Recovered",
                f"Successfully made {freed_count} vendor folders Online-Only!\n"
                "Hard drive space has been recovered."
            )

        self._set_controls_running(False)
        self.after(0, self._update_leftover_badge)

if __name__ == "__main__":
    cleanup_old_executable()
    app = QCBatchLoaderApp()
    app.mainloop()
