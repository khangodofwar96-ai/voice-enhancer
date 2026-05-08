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

st.set_page_config(page_title="AI Voice FX Editor", layout="wide")

st.title("🎛️ AI Voice FX Editor (Interactive Studio Mode)")
st.write("Turn effects ON/OFF, preview instantly, and export final audio")

uploaded_file = st.file_uploader(
    "Upload Audio/Video",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# ---------------------------
# AUDIO EXTRACTION
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
# CORE PROCESSOR (MODULAR FX)
# ---------------------------
def apply_fx(input_audio, output_audio, fx_settings):

    data, sr = sf.read(input_audio)

    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    data = data / (np.max(np.abs(data)) + 1e-6)

    effects = []

    # FX TOGGLE SYSTEM
    if fx_settings["highpass"]:
        effects.append(HighpassFilter(80))

    if fx_settings["lowpass"]:
        effects.append(LowpassFilter(12000))

    if fx_settings["noise_gate"]:
        effects.append(NoiseGate(threshold_db=-40, ratio=2))

    if fx_settings["compressor"]:
        effects.append(Compressor(
            threshold_db=-18,
            ratio=3,
            attack_ms=10,
            release_ms=150
        ))

    if fx_settings["gain"]:
        effects.append(Gain(2.5))

    if fx_settings["reverb"]:
        effects.append(Reverb(
            room_size=0.02,
            wet_level=0.02,
            dry_level=0.98
        ))

    if fx_settings["limiter"]:
        effects.append(Limiter(threshold_db=-1))

    board = Pedalboard(effects)

    processed = board(data, sr)

    processed = processed / (np.max(np.abs(processed)) + 1e-6)
    processed = processed * 0.95

    sf.write(output_audio, processed, sr)

# ---------------------------
# UI EFFECT CONTROLS
# ---------------------------
st.sidebar.header("🎚️ FX Controls")

fx_settings = {
    "highpass": st.sidebar.checkbox("High Pass Filter (Clean bass rumble)", True),
    "lowpass": st.sidebar.checkbox("Low Pass Filter (Smooth highs)", True),
    "noise_gate": st.sidebar.checkbox("Noise Gate (Remove background noise)", True),
    "compressor": st.sidebar.checkbox("Compressor (Level voice)", True),
    "gain": st.sidebar.checkbox("Gain Boost (Loudness)", True),
    "reverb": st.sidebar.checkbox("Light Reverb (Studio depth)", False),
    "limiter": st.sidebar.checkbox("Limiter (Prevent distortion)", True),
}

# ---------------------------
# PROCESS BUTTON
# ---------------------------
if uploaded_file:

    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully")

    is_video = uploaded_file.name.endswith(("mp4", "mov", "avi"))

    input_audio = "temp/input.wav"
    output_audio = "outputs/preview.wav"

    if is_video:
        with st.spinner("Extracting audio..."):
            extract_audio(file_path, input_audio)
    else:
        input_audio = file_path

    if st.button("🎧 Apply Selected Effects & Preview"):

        with st.spinner("Processing audio with selected FX..."):
            apply_fx(input_audio, output_audio, fx_settings)

        st.success("Preview ready!")

        st.subheader("🎙️ Original")
        st.audio(input_audio)

        st.subheader("✨ Processed Preview")
        st.audio(output_audio)

    st.divider()

    # FINAL EXPORT
    if st.button("⬇ Export Final Version"):

        final_output = "outputs/final.wav"

        apply_fx(input_audio, final_output, fx_settings)

        with open(final_output, "rb") as f:
            st.download_button(
                "Download Final Audio",
                f,
                file_name="studio_final.wav"
            )
