import os
import subprocess
import streamlit as st
import moviepy.editor as mp
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

# Create folders
os.makedirs("temp", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Streamlit config
st.set_page_config(
    page_title="AI Professional Voice Enhancer",
    layout="wide"
)

st.title("🎙️ AI Professional Voice Enhancer")
st.write("Upload rough audio/video and get studio-level enhanced sound.")

# Upload file
uploaded_file = st.file_uploader(
    "Upload Video or Audio",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# Extract audio
def extract_audio(video_path, output_audio):

    video = mp.VideoFileClip(video_path)

    video.audio.write_audiofile(
        output_audio,
        codec="pcm_s16le"
    )

# AI enhancement using DeepFilterNet
def ai_clean_audio(input_audio):

    command = [
        "deepFilter",
        input_audio,
        "--output-dir",
        "outputs"
    ]

    subprocess.run(command)

    enhanced_path = os.path.join(
        "outputs",
        os.path.basename(input_audio)
    )

    return enhanced_path

# Studio mastering
def studio_master(input_audio, output_audio):

    audio, sample_rate = sf.read(input_audio)

    # Convert stereo to mono if needed
    if len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)

    # Professional audio chain
    board = Pedalboard([

        # Clean rumble
        HighpassFilter(cutoff_frequency_hz=80),

        # Remove harsh highs
        LowpassFilter(cutoff_frequency_hz=12000),

        # Noise gate
        NoiseGate(
            threshold_db=-35,
            ratio=2
        ),

        # Compression
        Compressor(
            threshold_db=-18,
            ratio=4,
            attack_ms=5,
            release_ms=100
        ),

        # Voice presence
        Gain(gain_db=4),

        # Soft room feel
        Reverb(
            room_size=0.03,
            damping=0.2,
            wet_level=0.03,
            dry_level=0.97
        ),

        # Prevent clipping
        Limiter(threshold_db=-1)

    ])

    processed = board(audio, sample_rate)

    # Loudness normalization
    max_val = np.max(np.abs(processed))

    if max_val > 0:
        processed = processed / max_val * 0.95

    sf.write(output_audio, processed, sample_rate)

# Merge audio back into video
def merge_audio_video(video_path, audio_path, output_path):

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-i",
        audio_path,
        "-c:v",
        "copy",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        output_path
    ]

    subprocess.run(command)

# Main app
if uploaded_file:

    file_path = os.path.join(
        "temp",
        uploaded_file.name
    )

    # Save upload
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    input_audio = "temp/input.wav"
    mastered_audio = "outputs/mastered_voice.wav"

    is_video = uploaded_file.name.endswith(
        ("mp4", "mov", "avi")
    )

    # Extract audio if video
    if is_video:

        with st.spinner("Extracting audio from video..."):
            extract_audio(
                file_path,
                input_audio
            )

    else:
        input_audio = file_path

    # AI enhancement
    with st.spinner("Running AI voice enhancement..."):

        enhanced_audio = ai_clean_audio(
            input_audio
        )

    # Studio mastering
    with st.spinner("Applying studio mastering..."):

        studio_master(
            enhanced_audio,
            mastered_audio
        )

    st.success("Professional enhancement completed!")

    # Audio comparison
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Audio")
        st.audio(input_audio)

    with col2:
        st.subheader("Enhanced Audio")
        st.audio(mastered_audio)

    # Download section
    if is_video:

        final_video = "outputs/final_video.mp4"

        with st.spinner("Merging enhanced audio into video..."):

            merge_audio_video(
                file_path,
                mastered_audio,
                final_video
            )

        with open(final_video, "rb") as file:

            st.download_button(
                label="Download Enhanced Video",
                data=file,
                file_name="professional_voice_video.mp4",
                mime="video/mp4"
            )

    else:

        with open(mastered_audio, "rb") as file:

            st.download_button(
                label="Download Enhanced Audio",
                data=file,
                file_name="professional_voice.wav",
                mime="audio/wav"
            )
