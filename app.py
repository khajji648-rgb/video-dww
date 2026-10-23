import os
import sys
import threading
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from downloader import extract_video_info, download_video, QUALITY_FORMATS

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("محمل الفيديوهات بأعلى جودة - Video Downloader Pro")
        self.root.geometry("680x560")
        self.root.minsize(620, 500)

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Colors & Fonts
        bg_color = "#f4f6f9"
        self.root.configure(bg=bg_color)
        
        self.primary_font = ("Segoe UI", 10)
        self.header_font = ("Segoe UI", 12, "bold")
        self.title_font = ("Segoe UI", 16, "bold")

        default_download_dir = str(Path.home() / "Downloads" / "VideoDownloader")
        self.output_dir_var = tk.StringVar(value=default_download_dir)
        self.quality_var = tk.StringVar(value=list(QUALITY_FORMATS.keys())[0])
        self.status_var = tk.StringVar(value="جاهز. حط رابط الفيديو وضغط على 'فحص الرابط'.")
        self.progress_percent_var = tk.StringVar(value="0%")

        self._build_ui()

    def _build_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#1e293b", pady=15)
        header_frame.pack(fill=tk.X)

        title_lbl = tk.Label(
            header_frame, 
            text="🎬 محمل الفيديوهات الذكي - أعلى جودة", 
            font=self.title_font, 
            fg="#ffffff", 
            bg="#1e293b"
        )
        title_lbl.pack()

        subtitle_lbl = tk.Label(
            header_frame, 
            text="يدعم يوتيوب، فيسبوك، تيك توك، تويتر/X والمئات من المواقع", 
            font=("Segoe UI", 9), 
            fg="#94a3b8", 
            bg="#1e293b"
        )
        subtitle_lbl.pack(pady=(2, 0))

        # Main container
        main_frame = tk.Frame(self.root, bg="#f4f6f9", padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. URL Section
        url_lbl = tk.Label(main_frame, text="رابط الفيديو أو الموقع (URL):", font=self.header_font, bg="#f4f6f9", fg="#0f172a")
        url_lbl.pack(anchor="w")

        url_box = tk.Frame(main_frame, bg="#f4f6f9")
        url_box.pack(fill=tk.X, pady=(5, 10))

        self.url_entry = ttk.Entry(url_box, font=("Segoe UI", 10))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)

        paste_btn = tk.Button(url_box, text="📋 لصق", font=self.primary_font, bg="#e2e8f0", relief=tk.FLAT, padx=10, command=self._paste_clipboard)
        paste_btn.pack(side=tk.LEFT, padx=(6, 4))

        self.check_btn = tk.Button(url_box, text="🔍 فحص الرابط", font=self.primary_font, bg="#3b82f6", fg="#ffffff", relief=tk.FLAT, padx=12, command=self._start_inspect)
        self.check_btn.pack(side=tk.LEFT)

        # 2. Video Info Card
        self.info_frame = tk.LabelFrame(main_frame, text="معلومات الفيديو", font=self.primary_font, bg="#ffffff", padx=15, pady=10)
        self.info_frame.pack(fill=tk.X, pady=(5, 10))

        self.info_title_lbl = tk.Label(self.info_frame, text="العنوان: لم يتم فحص أي رابط بعد", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#ffffff", wraplength=580, justify=tk.LEFT)
        self.info_title_lbl.pack(anchor="w")

        self.info_extra_lbl = tk.Label(self.info_frame, text="الناشر: - | المدة: -", font=("Segoe UI", 9), fg="#64748b", bg="#ffffff")
        self.info_extra_lbl.pack(anchor="w", pady=(3, 0))

        # 3. Settings (Quality & Save Path)
        settings_frame = tk.Frame(main_frame, bg="#f4f6f9")
        settings_frame.pack(fill=tk.X, pady=5)

        # Quality
        q_frame = tk.Frame(settings_frame, bg="#f4f6f9")
        q_frame.pack(fill=tk.X, pady=3)
        tk.Label(q_frame, text="الجودة المطلوبة:", font=self.primary_font, bg="#f4f6f9").pack(side=tk.LEFT)
        self.quality_menu = ttk.Combobox(q_frame, textvariable=self.quality_var, values=list(QUALITY_FORMATS.keys()), state="readonly", width=42)
        self.quality_menu.pack(side=tk.LEFT, padx=10)

        # Output Folder
        folder_frame = tk.Frame(settings_frame, bg="#f4f6f9")
        folder_frame.pack(fill=tk.X, pady=3)
        tk.Label(folder_frame, text="مجلد الحفظ:", font=self.primary_font, bg="#f4f6f9").pack(side=tk.LEFT)
        folder_entry = ttk.Entry(folder_frame, textvariable=self.output_dir_var, font=("Segoe UI", 9))
        folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, ipady=2)
        browse_btn = tk.Button(folder_frame, text="تغيير...", font=("Segoe UI", 8), bg="#e2e8f0", relief=tk.FLAT, command=self._browse_folder)
        browse_btn.pack(side=tk.LEFT)

        # 4. Progress and Status
        progress_frame = tk.Frame(main_frame, bg="#f4f6f9")
        progress_frame.pack(fill=tk.X, pady=(15, 5))

        self.status_lbl = tk.Label(progress_frame, textvariable=self.status_var, font=("Segoe UI", 9), fg="#0f172a", bg="#f4f6f9", anchor="w")
        self.status_lbl.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(4, 2))

        self.percent_lbl = tk.Label(progress_frame, textvariable=self.progress_percent_var, font=("Segoe UI", 8), fg="#64748b", bg="#f4f6f9", anchor="e")
        self.percent_lbl.pack(fill=tk.X)

        # 5. Action Buttons
        btn_frame = tk.Frame(main_frame, bg="#f4f6f9")
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        self.download_btn = tk.Button(
            btn_frame, 
            text="⬇️ تحميل الفيديو الآن", 
            font=self.header_font, 
            bg="#10b981", 
            fg="#ffffff", 
            activebackground="#059669",
            relief=tk.FLAT, 
            pady=8,
            command=self._start_download
        )
        self.download_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        open_folder_btn = tk.Button(
            btn_frame, 
            text="📂 فتح مجلد التحميلات", 
            font=self.primary_font, 
            bg="#e2e8f0", 
            relief=tk.FLAT, 
            pady=8,
            command=self._open_downloads_folder
        )
        open_folder_btn.pack(side=tk.LEFT)

    def _paste_clipboard(self):
        try:
            clipboard_text = self.root.clipboard_get().strip()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        except Exception:
            pass

    def _browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if folder:
            self.output_dir_var.set(folder)

    def _open_downloads_folder(self):
        folder = self.output_dir_var.get()
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
        if sys.platform == 'win32':
            os.startfile(folder)
        else:
            subprocess.Popen(['xdg-open', folder])

    def _start_inspect(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("تنبيه", "عفاك دخل رابط أولاً.")
            return

        self.check_btn.config(state=tk.DISABLED)
        self.status_var.set("جاري استخراج معلومات الرابط...")

        def run_thread():
            try:
                info = extract_video_info(url)
                duration = info.get('duration', 0)
                dur_str = f"{duration // 60} د و {duration % 60} ث" if duration else "مباشر / غير معروف"
                
                title = info.get('title', 'غير معروف')
                uploader = info.get('uploader', 'غير معروف')
                
                def update_ui():
                    self.info_title_lbl.config(text=f"العنوان: {title}")
                    self.info_extra_lbl.config(text=f"الناشر: {uploader}  |  المدة: {dur_str}")
                    self.status_var.set("تم فحص الرابط بنجاح! اختار الجودة وضغط على 'تحميل الفيديو الآن'.")
                    self.check_btn.config(state=tk.NORMAL)

                self.root.after(0, update_ui)
            except Exception as e:
                def on_error():
                    messagebox.showerror("خطأ", f"تعذر استخراج معلومات هاد الرابط:\n{e}")
                    self.status_var.set("فشل استخراج معلومات الرابط.")
                    self.check_btn.config(state=tk.NORMAL)

                self.root.after(0, on_error)

        threading.Thread(target=run_thread, daemon=True).start()

    def _start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("تنبيه", "عفاك دخل رابط الفيديو أولاً.")
            return

        self.download_btn.config(state=tk.DISABLED)
        self.check_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_percent_var.set("0%")
        self.status_var.set("جاري بدء التحميل بأعلى جودة...")

        out_dir = self.output_dir_var.get()
        quality_key = self.quality_var.get()

        def progress_hook(d):
            status = d.get('status')
            if status == 'downloading':
                total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
                downloaded_bytes = d.get('downloaded_bytes', 0)
                speed = d.get('speed', 0)
                speed_str = f"{speed / (1024 * 1024):.2f} MB/s" if speed else "حساب السرعة..."
                
                if total_bytes > 0:
                    percent = (downloaded_bytes / total_bytes) * 100
                    def update_prog():
                        self.progress_bar['value'] = percent
                        self.progress_percent_var.set(f"{percent:.1f}%")
                        self.status_var.set(f"جاري التحميل... السرعة: {speed_str}")
                    self.root.after(0, update_prog)
                else:
                    def update_prog_indeterminate():
                        self.progress_bar.step(2)
                        self.status_var.set(f"جاري التحميل... ({downloaded_bytes // (1024*1024)} MB تم تحميلها)")
                    self.root.after(0, update_prog_indeterminate)
            elif status == 'finished':
                def on_finished():
                    self.status_var.set("تم اكتمال تنزيل أجزاء الفيديو! جاري المعالجة والدمج (Merging)...")
                    self.progress_bar['value'] = 100
                    self.progress_percent_var.set("100%")
                self.root.after(0, on_finished)

        def run_download():
            try:
                download_video(url, out_dir, quality_key, progress_callback=progress_hook)
                def on_success():
                    self.status_var.set("اكتمل التحميل بنجاح وتم حفظ الملف!")
                    self.download_btn.config(state=tk.NORMAL)
                    self.check_btn.config(state=tk.NORMAL)
                    messagebox.showinfo("تم بنجاح", f"مبروك! تم تحميل الفيديو وحفظه فالمجلد:\n{out_dir}")
                self.root.after(0, on_success)
            except Exception as e:
                def on_error():
                    self.status_var.set("وقع خطأ أثناء التحميل.")
                    self.download_btn.config(state=tk.NORMAL)
                    self.check_btn.config(state=tk.NORMAL)
                    messagebox.showerror("خطأ في التحميل", f"وقع خطأ:\n{e}")
                self.root.after(0, on_error)

        threading.Thread(target=run_download, daemon=True).start()

def main():
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
