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

st.set_page_config(page_title="AI Voice Studio Pro", layout="wide")

st.title("🎙️ AI Studio Voice Enhancer (Pro Edition)")
st.write("Upload audio/video → get professional studio voice with visible effect chain")

uploaded_file = st.file_uploader(
    "Upload File",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# ----------------------------
# SHOW EFFECT CHAIN UI
# ----------------------------
st.subheader("🎛️ Effect Chain (Applied in Order)")

st.markdown("""
### 🧠 Processing Pipeline

1. 🎧 High-Pass Filter (Remove rumble below 80Hz)
2. 🎧 Low-Pass Filter (Remove harsh highs above 12kHz)
3. 🚪 Noise Gate (Remove background noise)
4. 🎚️ Compressor (Level voice consistency)
5. 🔊 Gain Boost (Increase clarity)
6. 🌫️ Reverb (Very light studio depth)
7. 🚫 Limiter (Prevent distortion)
8. 📦 Normalize (Final loudness balancing)
""")

st.divider()

# ----------------------------
# AUDIO EXTRACTION
# ----------------------------
def extract_audio(video_path, audio_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        audio_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ----------------------------
# AUDIO PROCESSING
# ----------------------------
def clean_audio(input_audio, output_audio):

    st.info("🎧 Step 1: Loading audio")
    data, sr = sf.read(input_audio)

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    st.success("✔ Audio loaded")

    st.info("🎚️ Step 2: Applying normalization")
    data = data / (np.max(np.abs(data)) + 1e-6)

    st.info("🎛️ Step 3: Applying studio effects")

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

    st.success("✔ Effects applied successfully")

    st.info("📦 Step 4: Final normalization")

    processed = processed / (np.max(np.abs(processed)) + 1e-6)
    processed = processed * 0.95

    sf.write(output_audio, processed, sr)

    st.success("🎉 Studio mastering complete!")

# ----------------------------
# MERGE VIDEO
# ----------------------------
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

# ----------------------------
# MAIN FLOW
# ----------------------------
if uploaded_file:

    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("📁 File uploaded successfully")

    is_video = uploaded_file.name.endswith(("mp4", "mov", "avi"))

    input_audio = "temp/input.wav"
    output_audio = "outputs/clean.wav"

    if is_video:
        with st.spinner("🎥 Extracting audio from video..."):
            extract_audio(file_path, input_audio)
    else:
        input_audio = file_path

    # PROCESS
    with st.spinner("🤖 Enhancing audio with studio chain..."):
        clean_audio(input_audio, output_audio)

    st.divider()

    # BEFORE / AFTER
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎙️ Original Audio")
        st.audio(input_audio)

    with col2:
        st.subheader("✨ Enhanced Audio (Studio)")
        st.audio(output_audio)

    st.divider()

    # VIDEO MERGE
    if is_video:

        final_video = "outputs/final.mp4"

        with st.spinner("🎬 Merging enhanced audio with video..."):
            merge(file_path, output_audio, final_video)

        st.success("🎬 Final video ready!")

        with open(final_video, "rb") as f:
            st.download_button(
                "⬇ Download Enhanced Video",
                f,
                file_name="studio_voice_video.mp4"
            )

    else:

        with open(output_audio, "rb") as f:
            st.download_button(
                "⬇ Download Enhanced Audio",
                f,
                file_name="studio_voice.wav"
            )
