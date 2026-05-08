import streamlit as st
from pedalboard import Pedalboard, Compressor, Gain, NoiseGate, HighPassFilter
from pedalboard.io import AudioFile
import io

st.title("Studio Voice Converter")

uploaded_file = st.file_uploader("Upload your rough recording", type=['wav', 'mp3'])

if uploaded_file:
    # 1. Read the audio
    with AudioFile(uploaded_file) as f:
        audio = f.read(f.frames)
        samplerate = f.samplerate

    # 2. Define the "Studio" Chain
    board = Pedalboard([
        NoiseGate(threshold_db=-30),
        HighPassFilter(cutoff_frequency_hz=80), # Removes low-end rumble
        Compressor(threshold_db=-16, ratio=4),  # Evens out the voice
        Gain(gain_db=2)                         # Brings back the volume
    ])

    # 3. Process
    effected = board(audio, samplerate)

    # 4. Output
    st.audio(effected, sample_rate=samplerate)
    st.success("Voice enhanced!")
