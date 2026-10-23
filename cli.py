import sys
from pathlib import Path
from downloader import extract_video_info, download_video, QUALITY_FORMATS

def main():
    print("=" * 60)
    print("       🎬 أداة استخراج وتحميل الفيديوهات بأعلى جودة       ")
    print("=" * 60)
    
    default_dir = str(Path.home() / "Downloads" / "VideoDownloader")

    while True:
        url = input("\n[?] دخل رابط الفيديو أو الموقع (أو 'q' للخروج): ").strip()
        if not url:
            continue
        if url.lower() in ['q', 'quit', 'exit']:
            print("بالسلامة!")
            sys.exit(0)

        print("\n[+] جاري فحص الرابط واستخراج المعلومات...")
        try:
            info = extract_video_info(url)
            duration = info.get('duration', 0)
            dur_str = f"{duration // 60} د و {duration % 60} ث" if duration else "غير معروف"
            print(f"[✓] العنوان: {info.get('title')}")
            print(f"[✓] الناشر : {info.get('uploader')}")
            print(f"[✓] المدة  : {dur_str}")
        except Exception as e:
            print(f"[-] خطأ أثناء فحص الرابط: {e}")
            continue

        print("\nخيارات الجودة المتوفرة:")
        options = list(QUALITY_FORMATS.keys())
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt}")

        choice = input("\nاختار رقم الجودة (اضغط Enter للاختيار الافتراضي [1]): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            selected_quality = options[int(choice) - 1]
        else:
            selected_quality = options[0]

        print(f"[+] اخترت: {selected_quality}")
        print(f"[+] مسار الحفظ الافتراضي: {default_dir}")
        custom_dir = input("بغيتي تغير مسار الحفظ؟ (خليه خاوي للاحتفاظ به): ").strip()
        out_dir = custom_dir if custom_dir else default_dir

        print("\n[+] كيبدا التحميل دابا...")
        try:
            download_video(url, out_dir, selected_quality)
            print(f"\n[✓] تم التحميل بنجاح وحفظ الملف في: {out_dir}\n")
        except Exception as e:
            print(f"\n[-] وقع خطأ أثناء التحميل: {e}\n")

if __name__ == '__main__':
    main()
