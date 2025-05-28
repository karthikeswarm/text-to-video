import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import TextClip, AudioFileClip
import os
import textwrap
import uuid

# Split large text into manageable chunks for TTS
def split_text(text, max_chars=4500):
    return textwrap.wrap(text, max_chars, break_long_words=False, replace_whitespace=False)

# Generate audio from text chunks and combine
def text_to_audio(text, output_path="output_audio.mp3"):
    chunks = split_text(text)
    combined = AudioSegment.empty()

    for i, chunk in enumerate(chunks):
        tts = gTTS(chunk)
        temp_path = f"chunk_{uuid.uuid4().hex}.mp3"
        tts.save(temp_path)
        combined += AudioSegment.from_mp3(temp_path)
        os.remove(temp_path)

    combined.export(output_path, format="mp3")
    return output_path

# Create a video with audio and overlaid text
def create_video_with_audio(text, audio_path, video_path="output_video.mp4"):
    audio_clip = AudioFileClip(audio_path)
    text_clip = TextClip(
        txt=text,
        fontsize=24,
        color='white',
        size=(640, 480),
        method='caption',
        bg_color='black',
        duration=audio_clip.duration
    )
    video = text_clip.set_audio(audio_clip)
    video.write_videofile(video_path, fps=24, codec='libx264', audio_codec='aac')
    return video_path

# Streamlit UI
st.set_page_config(page_title="Text to Video Generator", layout="centered")
st.title("📽️ Text to Video with Audio Generator")

text = st.text_area("Enter your text here:", height=300)

if st.button("Generate Video"):
    if not text.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Generating audio and video..."):
            audio_file = text_to_audio(text, "output_audio.mp3")
            video_file = create_video_with_audio(text, audio_file, "output_video.mp4")

        st.success("Generation complete!")
        st.video(video_file)
        st.audio(audio_file)
        st.download_button("⬇️ Download Audio", open(audio_file, 'rb'), file_name="narration.mp3", mime="audio/mpeg")
