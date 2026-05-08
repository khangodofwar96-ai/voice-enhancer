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

st.set_page_config(page_title="AI Auto Studio Voice", layout="wide")

st.title("🎙️ AI Auto Studio Voice Enhancer")
st.write("Upload audio/video → AI automatically analyzes and applies professional mastering")

uploaded_file = st.file_uploader(
    "Upload File",
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
# AUTO STUDIO ENGINE
# ---------------------------
def auto_master_audio(input_audio, output_audio):

    data, sr = sf.read(input_audio)

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Normalize input
    data = data / (np.max(np.abs(data)) + 1e-6)

    # ---------------------------
    # AUDIO ANALYSIS
    # ---------------------------
    rms = np.sqrt(np.mean(data**2))
    peak = np.max(np.abs(data))

    st.info(f"📊 Audio RMS Level: {rms:.4f}")
    st.info(f"📊 Peak Level: {peak:.4f}")

    effects = []

    # ---------------------------
    # SMART DECISION ENGINE
    # ---------------------------

    if rms < 0.02:
        st.warning("🔍 Detected: Low-quality / noisy audio")
        effects.append(NoiseGate(threshold_db=-45, ratio=3))
        effects.append(Compressor(threshold_db=-25, ratio=5))
        effects.append(Gain(3.0))

    elif 0.02 <= rms < 0.1:
        st.success("🔍 Detected: Normal voice audio")
        effects.append(NoiseGate(threshold_db=-40, ratio=2))
        effects.append(Compressor(threshold_db=-18, ratio=3))
        effects.append(Gain(2.0))

    else:
        st.warning("🔍 Detected: Loud / compressed audio")
        effects.append(Limiter(threshold_db=-2))
        effects.append(Compressor(threshold_db=-20, ratio=4))

    # ---------------------------
    # ALWAYS APPLY STUDIO MASTERING
    # ---------------------------

    effects += [
        HighpassFilter(80),
        LowpassFilter(12000),
        Reverb(room_size=0.015, wet_level=0.02, dry_level=0.98),
        Limiter(threshold_db=-1)
    ]

    board = Pedalboard(effects)

    processed = board(data, sr)

    # Final normalization
    processed = processed / (np.max(np.abs(processed)) + 1e-6)
    processed = processed * 0.95

    sf.write(output_audio, processed, sr)

    st.success("🎧 Auto Studio Mastering Completed")

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
        with st.spinner("Extracting audio..."):
            extract_audio(file_path, input_audio)
    else:
        input_audio = file_path

    # Run AI auto mastering
    with st.spinner("AI analyzing and enhancing audio..."):
        auto_master_audio(input_audio, output_audio)

    st.divider()

    # Preview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ Original Audio")
        st.audio(input_audio)

    with col2:
        st.subheader("✨ AI Enhanced Audio")
        st.audio(output_audio)

    st.divider()

    # Video merge
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
                file_name="auto_studio_video.mp4"
            )

    else:

        with open(output_audio, "rb") as f:
            st.download_button(
                "⬇ Download Enhanced Audio",
                f,
                file_name="auto_studio_audio.wav"
            )
