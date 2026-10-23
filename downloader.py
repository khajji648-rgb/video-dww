import os
import yt_dlp

QUALITY_FORMATS = {
    "أعلى جودة ممكنة (Best Quality / 4K / 1080p)": "bestvideo+bestaudio/best",
    "جودة عالية (1080p Max)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "جودة متوسطة (720p Max)": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "صوت فقط (Audio Only - Best Quality)": "bestaudio/best",
}

def extract_video_info(url: str):
    """
    استخراج معلومات الفيديو دون تحميله
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        # Handle playlists or single videos
        if 'entries' in info:
            entries = list(info['entries'])
            first_entry = entries[0] if entries else {}
            return {
                'is_playlist': True,
                'playlist_count': len(entries),
                'title': info.get('title', 'قائمة تشغيل'),
                'duration': first_entry.get('duration', 0),
                'uploader': info.get('uploader', 'غير معروف'),
                'thumbnail': first_entry.get('thumbnail', None),
            }
        else:
            return {
                'is_playlist': False,
                'title': info.get('title', 'فيديو بدون عنوان'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'غير معروف'),
                'thumbnail': info.get('thumbnail', None),
            }

def download_video(url: str, output_path: str, quality_key: str = None, progress_callback=None):
    """
    تحميل الفيديو بأعلى جودة أو بالجودة المختارة
    """
    if not os.path.exists(output_path):
        os.makedirs(output_path, exist_ok=True)

    fmt = QUALITY_FORMATS.get(quality_key, "bestvideo+bestaudio/best")

    def yt_hook(d):
        if progress_callback:
            progress_callback(d)

    is_audio_only = (quality_key == "صوت فقط (Audio Only - Best Quality)")

    ydl_opts = {
        'format': fmt,
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'progress_hooks': [yt_hook],
        'no_warnings': True,
        'ignoreerrors': False,
    }

    if is_audio_only:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        ydl_opts['merge_output_format'] = 'mp4'

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
