import os
import subprocess
import streamlit as st
from moviepy.editor import VideoFileClip
from pedalboard import Pedalboard, Compressor, NoiseGate, Reverb, Gain
from pedalboard.io import AudioFile
import soundfile as sf
import noisereduce as nr
import numpy as np

os.makedirs("temp", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

st.set_page_config(page_title="AI Voice Editor", layout="wide")

st.title("🎙️ AI Voice Studio Enhancer")
st.write("Upload rough audio/video and convert it into studio-quality voice.")

uploaded_file = st.file_uploader(
    "Upload Video or Audio",
    type=["mp4", "mov", "avi", "wav", "mp3"]
)


def extract_audio(video_path, output_audio):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio)



def enhance_audio(input_audio, output_audio):
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

    effected = board(reduced_noise, rate)

    sf.write(output_audio, effected, rate)


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
            )
