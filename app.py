import argparse
import os
import tempfile
import time
from functools import wraps

import streamlit as st

from audio_to_text import transcribe_audio
from text_summary import (align_chapters, get_automatic_chapters,
                          summarize_chapters)
from youtube_extraction import get_youtube_chapters, youtube_to_audio


def timing_decorator(message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                st.write(f"{message} complete - {end_time - start_time:.2f}s")
                return result

        return wrapper

    return decorator


@timing_decorator("Downloading Youtube video")
def download_youtube(youtube_url, work_dir):
    audio_fpath = youtube_to_audio(youtube_url, work_dir)
    # Get Youtube chapters, return empty list if is not in metadata
    yt_chapters = get_youtube_chapters(youtube_url)
    return audio_fpath, yt_chapters


@timing_decorator("Transcribing audio")
def audio_to_text(audio_fpath):
    # Transcribe video with Whisper
    timestamped_text = transcribe_audio(audio_fpath)
    return timestamped_text


@timing_decorator("Retrieving chapters")
def retrieve_chapters(timestamped_text, yt_chapters):
    # Get chapters
    if len(yt_chapters) == 0:
        chapters = get_automatic_chapters(timestamped_text)
    else:
        chapters = align_chapters(timestamped_text, yt_chapters)
    return chapters


@timing_decorator("Summarizing video")
def summarize_youtube_chapters(chapters):
    # Summarize chapters
    summarized_chapters = summarize_chapters(chapters)
    return summarized_chapters


def get_work_dir():
    temp_dir = tempfile.TemporaryDirectory()
    work_dir = temp_dir.name
    return work_dir


def convert_seconds(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int((seconds % 3600) % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def summarize_video(youtube_url):
    st.video(youtube_url)
    # Create a temporary directory to store the audio file
    work_dir = get_work_dir()

    # Summarize the video
    audio_fpath, yt_chapters = download_youtube(youtube_url, work_dir)
    timestamped_text = audio_to_text(audio_fpath)

    chapters = retrieve_chapters(timestamped_text, yt_chapters)
    summarized_chapters, overall_summary = summarize_youtube_chapters(chapters)

    st.write(f"**TLDR:** {overall_summary}")

    for summarized_chapter in summarized_chapters:
        start_time = convert_seconds(summarized_chapter["start"])
        end_time = convert_seconds(summarized_chapter["end"])

        timestamp = f"{start_time} - {end_time}"
        title = summarized_chapter["title"]
        summary = summarized_chapter["summary"]

        # Display the hyperlink with timestamp and title
        hyperlink = (
            f"[{timestamp} - {title}]({youtube_url}&t={summarized_chapter['start']}s)"
        )
        st.markdown(hyperlink, unsafe_allow_html=True)

        st.write(summary)


def app():
    st.title("Video Summarizer")
    youtube_url = st.text_input("Enter a YouTube URL")

    # Add summarize button
    summarize_button = st.button("Summarize")

    if summarize_button:
        summarize_video(youtube_url)


if __name__ == "__main__":
    app()
