import streamlit as st
from pedalboard import Pedalboard, Compressor, Gain, NoiseGate, HighPassFilter, Reverb
from pedalboard.io import AudioFile
import io
import numpy as np

st.set_page_config(page_title="Studio Voice AI", page_icon="🎙️")

st.title("🎙️ AI Studio Voice Enhancer")
st.write("Upload a rough recording to automatically apply studio-grade processing.")

uploaded_file = st.file_uploader("Upload Audio (wav, mp3, m4a)", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    st.subheader("1. Original Audio")
    st.audio(uploaded_file)
    
    with st.spinner("✨ Enhancing your voice..."):
        try:
            # Read the audio file
            with AudioFile(uploaded_file) as f:
                audio = f.read(f.frames)
                samplerate = f.samplerate

            # Define the Studio Processing Chain
            # This mimics a professional vocal strip
            board = Pedalboard([
                # 1. Remove background noise floor
                NoiseGate(threshold_db=-35), 
                # 2. Remove low-end 'thumps' and rumble
                HighPassFilter(cutoff_frequency_hz=80), 
                # 3. Dynamic Compression (The 'Studio' sound)
                Compressor(threshold_db=-18, ratio=4), 
                # 4. Subtle warmth/room feel
                Reverb(room_size=0.1, dry_level=0.8, wet_level=0.1),
                # 5. Final volume boost
                Gain(gain_db=4) 
            ])

            # Process the audio
            effected = board(audio, samplerate)

            # Write to an in-memory buffer (so we don't need disk space)
            buffer = io.BytesIO()
            with AudioFile(buffer, 'w', samplerate, effected.shape[0]) as f:
                f.write(effected)
            
            st.success("✅ Processing Complete!")
            
            st.subheader("2. Studio Quality Audio")
            st.audio(buffer)
            
            st.download_button(
                label="Download Enhanced Audio",
                data=buffer.getvalue(),
                file_name="studio_enhanced.wav",
                mime="audio/wav"
            )

        except Exception as e:
            st.error(f"Processing error: {e}")
            st.info("Try uploading a standard .wav or .mp3 file.")

else:
    st.info("Please upload an audio file to begin.")
