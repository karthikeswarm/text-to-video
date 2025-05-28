import streamlit as st
from gtts import gTTS
from moviepy.config import change_settings
from moviepy.editor import TextClip, AudioFileClip
import os
import textwrap
import uuid
import shutil

# --- Configure MoviePy to find ImageMagick ---
# Change this path to where your ImageMagick magick.exe is installed
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

# --- Utility Functions ---

def split_text(text, max_chars=4500):
    """Split long text into smaller chunks for gTTS."""
    return textwrap.wrap(text, max_chars, break_long_words=False, replace_whitespace=False)

def text_to_audio(text, output_path="output_audio.mp3"):
    """Convert long text into a single audio file using gTTS."""
    chunks = split_text(text)
    temp_files = []

    for i, chunk in enumerate(chunks):
        tts = gTTS(chunk)
        temp_path = f"temp_{uuid.uuid4().hex}.mp3"
        tts.save(temp_path)
        temp_files.append(temp_path)

    if len(temp_files) == 1:
        shutil.move(temp_files[0], output_path)
    else:
        with open("file_list.txt", "w") as f:
            for file in temp_files:
                f.write(f"file '{file}'\n")
        os.system(f"ffmpeg -f concat -safe 0 -i file_list.txt -c copy {output_path}")
        os.remove("file_list.txt")
        for file in temp_files:
            os.remove(file)

    return output_path

def create_video_with_audio(text, audio_path, video_path="output_video.mp4"):
    """Create a video with text overlay and audio narration."""
    audio_clip = AudioFileClip(audio_path)

    try:
        text_clip = TextClip(
            text,
            fontsize=24,
            color='black',       # text color black
            size=(640, 480),
            method='caption',
            font='Arial',
            bg_color='white'     # background color white
        ).set_duration(audio_clip.duration)
    except Exception as e:
        st.error(f"Error creating text clip: {e}")
        return None

    video = text_clip.set_audio(audio_clip)
    video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
    return video_path

# --- Streamlit UI ---

st.set_page_config(page_title="Text to Video Generator", layout="centered")
st.title("🎙️ Text to Video with Audio Generator")

text = st.text_area("Enter your text (no length limit):", height=300)

if st.button("Generate Video"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating audio and video..."):
            audio_file = text_to_audio(text, "output_audio.mp3")
            video_file = create_video_with_audio(text, audio_file, "output_video.mp4")

        if video_file:
            st.success("✅ Generation complete!")
            st.video(video_file)
            st.audio(audio_file)
            st.download_button("⬇️ Download Audio", open(audio_file, 'rb'), file_name="narration.mp3", mime="audio/mpeg")
        else:
            st.error("Failed to generate video. Please check the error above.")
