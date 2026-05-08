import os
import streamlit as st
import subprocess
import soundfile as sf
import numpy as np

from pedalboard import (
    Pedalboard,
    Compressor,
    NoiseGate,
    Reverb,
    Gain,
    Limiter,
    HighpassFilter,
    LowpassFilter
)

os.makedirs("temp", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

st.set_page_config(page_title="AI Voice Studio", layout="wide")

st.title("🎙️ AI Studio Voice Enhancer (Stable Version)")
st.write("Upload audio or video → get clean, studio-like voice")

uploaded_file = st.file_uploader(
    "Upload file",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# ---------------------------
# Extract audio from video
# ---------------------------
def extract_audio(video_path, audio_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------------------
# AI-style cleanup (SAFE)
# ---------------------------
def clean_audio(input_audio, output_audio):

    data, sr = sf.read(input_audio)

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Normalize input
    data = data / (np.max(np.abs(data)) + 1e-6)

    board = Pedalboard([

        HighpassFilter(80),
        LowpassFilter(12000),

        NoiseGate(threshold_db=-40, ratio=2),

        Compressor(
            threshold_db=-18,
            ratio=3,
            attack_ms=10,
            release_ms=150
        ),

        Gain(2.5),

        Reverb(
            room_size=0.02,
            wet_level=0.02,
            dry_level=0.98
        ),

        Limiter(threshold_db=-1)

    ])

    processed = board(data, sr)

    processed = processed / (np.max(np.abs(processed)) + 1e-6)

    sf.write(output_audio, processed * 0.95, sr)

# ---------------------------
# Merge audio + video
# ---------------------------
def merge(video_path, audio_path, output_path):

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        output_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------------------
# MAIN APP
# ---------------------------
if uploaded_file:

    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully")

    is_video = uploaded_file.name.endswith(("mp4", "mov", "avi"))

    input_audio = "temp/input.wav"
    output_audio = "outputs/clean.wav"

    # Step 1: extract audio
    if is_video:
        with st.spinner("Extracting audio..."):
            extract_audio(file_path, input_audio)
    else:
        input_audio = file_path

    # Step 2: clean audio
    with st.spinner("Enhancing voice (AI processing)..."):
        clean_audio(input_audio, output_audio)

    st.success("Enhancement completed!")

    # Compare
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original")
        st.audio(input_audio)

    with col2:
        st.subheader("Enhanced")
        st.audio(output_audio)

    # Step 3: video merge
    if is_video:

        final_video = "outputs/final.mp4"

        with st.spinner("Merging audio with video..."):
            merge(file_path, output_audio, final_video)

        with open(final_video, "rb") as f:
            st.download_button(
                "Download Enhanced Video",
                f,
                file_name="studio_video.mp4"
            )

    else:

        with open(output_audio, "rb") as f:
            st.download_button(
                "Download Enhanced Audio",
                f,
                file_name="studio_audio.wav"
            )
