import glob

import yt_dlp


def youtube_to_audio(url, output_path, filename_template="youtube_video"):
    ydl_opts = {
        "outtmpl": f"{output_path}/{filename_template}",
        "format": "m4a/bestaudio/best",
        "postprocessors": [
            {  # Extract audio using ffmpeg
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
            }
        ],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    file_path = glob.glob(f"{output_path}/{filename_template}*")[0]
    return file_path


def get_youtube_chapters(url):
    video_chapters = []
    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if "chapters" in info and info["chapters"]:
            video_chapters = info["chapters"]

    return video_chapters
