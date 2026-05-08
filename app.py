import os
import subprocess
import streamlit as st
from moviepy.editor import VideoFileClip
from pedalboard import Pedalboard, Compressor, NoiseGate, Reverb, Gain
from pedalboard.io import AudioFile
import soundfile as sf
import noisereduce as nr
import numpy as np

# Create folders
os.makedirs("temp", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Streamlit page
st.set_page_config(
    page_title="AI Voice Enhancer",
    layout="wide"
)

st.title("🎙️ AI Voice Studio Enhancer")
st.write("Upload rough audio/video and convert it into studio-quality voice.")

# Upload file
uploaded_file = st.file_uploader(
    "Upload Video or Audio",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)

# Extract audio from video
def extract_audio(video_path, output_audio):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio)

# Enhance audio
def enhance_audio(input_audio, output_audio):

    # Read audio
    data, rate = sf.read(input_audio)

    # Convert stereo to mono
    if len(data.shape) > 1:
        data = np.mean(data, axis=1)

    # Noise reduction
    reduced_noise = nr.reduce_noise(
        y=data,
        sr=rate,
        prop_decrease=0.9
    )

    # Studio effects
    board = Pedalboard([
        NoiseGate(threshold_db=-30, ratio=1.5),
        Compressor(threshold_db=-20, ratio=4),
        Gain(gain_db=5),
        Reverb(room_size=0.05)
    ])

    # Apply effects
    effected = board(reduced_noise, rate)

    # Save enhanced audio
    sf.write(output_audio, effected, rate)

# Merge enhanced audio back into video
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

    # Save uploaded file
    file_path = os.path.join("temp", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("File uploaded successfully!")

    audio_input = "temp/input_audio.wav"
    enhanced_audio = "outputs/enhanced_audio.wav"

    # If video
    if uploaded_file.name.endswith(("mp4", "mov", "avi")):

        with st.spinner("Extracting audio..."):
            extract_audio(file_path, audio_input)

    else:
        audio_input = file_path

    # Enhance voice
    with st.spinner("Enhancing voice with AI..."):
        enhance_audio(audio_input, enhanced_audio)

    st.success("Voice enhancement completed!")

    # Before vs After
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Audio")
        st.audio(audio_input)

    with col2:
        st.subheader("Enhanced Audio")
        st.audio(enhanced_audio)

    # Download output
    if uploaded_file.name.endswith(("mp4", "mov", "avi")):

        final_video = "outputs/final_video.mp4"

        with st.spinner("Merging enhanced voice into video..."):
            merge_audio_video(
                file_path,
                enhanced_audio,
                final_video
            )

        with open(final_video, "rb") as file:
            st.download_button(
                label="Download Enhanced Video",
                data=file,
                file_name="studio_voice_video.mp4",
                mime="video/mp4"
            )

    else:

        with open(enhanced_audio, "rb") as file:
            st.download_button(
                label="Download Enhanced Audio",
                data=file,
                file_name="studio_voice.wav",
                mime="audio/wav"
            )
