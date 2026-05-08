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

# ---------------------------
# SETUP
# ---------------------------
os.makedirs("temp", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

st.set_page_config(page_title="AI Voice Enhancer Pro+", layout="wide")

st.title("🎙️ AI Voice Enhancer Pro+ (Better than VoiceEnhancer.ai)")
st.write("Upload audio/video → AI analyzes and upgrades your voice automatically")

uploaded_file = st.file_uploader(
    "Upload File",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# ---------------------------
# EXTRACT AUDIO
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
# SMART AI ENGINE
# ---------------------------
def ai_master_engine(input_audio, output_audio):

    data, sr = sf.read(input_audio)

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Normalize
    data = data / (np.max(np.abs(data)) + 1e-6)

    # ---------------------------
    # AUDIO ANALYSIS
    # ---------------------------
    rms = np.sqrt(np.mean(data**2))
    peak = np.max(np.abs(data))

    st.info(f"📊 RMS Level: {rms:.4f}")
    st.info(f"📊 Peak Level: {peak:.4f}")

    # ---------------------------
    # AI DECISION ENGINE
    # ---------------------------
    effects = []

    if rms < 0.02:
        st.warning("🔍 Detected: Low quality / noisy audio")
        effects += [
            NoiseGate(-45, ratio=3),
            Compressor(-25, ratio=5),
            Gain(3.5)
        ]

    elif rms < 0.1:
        st.success("🔍 Detected: Normal speech audio")
        effects += [
            NoiseGate(-40, ratio=2),
            Compressor(-18, ratio=3),
            Gain(2.0)
        ]

    else:
        st.warning("🔍 Detected: Loud / compressed audio")
        effects += [
            Limiter(-2),
            Compressor(-20, ratio=4)
        ]

    # ---------------------------
    # PROFESSIONAL MASTERING LAYER
    # ---------------------------
    effects += [
        HighpassFilter(80),
        LowpassFilter(12000),

        Reverb(
            room_size=0.015,
            wet_level=0.02,
            dry_level=0.98
        ),

        Limiter(-1)
    ]

    board = Pedalboard(effects)

    processed = board(data, sr)

    # Final normalization
    processed = processed / (np.max(np.abs(processed)) + 1e-6)
    processed = processed * 0.95

    sf.write(output_audio, processed, sr)

    st.success("🎧 AI Mastering Complete")

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
    output_audio = "outputs/final.wav"

    # Extract audio if needed
    if is_video:
        with st.spinner("Extracting audio from video..."):
            extract_audio(file_path, input_audio)
    else:
        input_audio = file_path

    # AI Processing
    with st.spinner("AI analyzing and enhancing audio..."):
        ai_master_engine(input_audio, output_audio)

    st.divider()

    # ---------------------------
    # BEFORE / AFTER
    # ---------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ Original Audio")
        st.audio(input_audio)

    with col2:
        st.subheader("✨ AI Enhanced Audio")
        st.audio(output_audio)

    st.divider()

    # ---------------------------
    # DOWNLOAD / VIDEO MERGE
    # ---------------------------
    if is_video:

        final_video = "outputs/final_video.mp4"

        subprocess.run([
            "ffmpeg", "-y",
            "-i", file_path,
            "-i", output_audio,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            final_video
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open(final_video, "rb") as f:
            st.download_button(
                "⬇ Download Enhanced Video",
                f,
                file_name="pro_voice_video.mp4"
            )

    else:

        with open(output_audio, "rb") as f:
            st.download_button(
                "⬇ Download Enhanced Audio",
                f,
                file_name="pro_voice_audio.wav"
            )
