import streamlit as st
import io
import numpy as np

# Try-except block to catch the exact moment the library fails
try:
    from pedalboard import Pedalboard, Compressor, Gain, NoiseGate, HighPassFilter, Reverb
    from pedalboard.io import AudioFile
except ImportError:
    st.error("The 'pedalboard' library is not installed yet. Please wait or reboot the app.")

st.set_page_config(page_title="AI Audio Studio", page_icon="🎙️")

st.title("🎙️ AI Studio Voice Enhancer")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Audio (WAV or MP3)", type=['wav', 'mp3'])

if uploaded_file is not None:
    # Play original
    st.write("### Original Recording")
    st.audio(uploaded_file)
    
    if st.button("✨ Apply Studio Effects"):
        with st.spinner("Processing..."):
            try:
                # 1. Read the audio into Pedalboard
                with AudioFile(uploaded_file) as f:
                    audio = f.read(f.frames)
                    samplerate = f.samplerate

                # 2. The Studio Chain
                # NoiseGate: Kills background hiss
                # HighPass: Removes desk thumps
                # Compressor: Makes it sound professional/thick
                # Reverb: Adds a tiny bit of space
                board = Pedalboard([
                    NoiseGate(threshold_db=-30),
                    HighPassFilter(cutoff_frequency_hz=100),
                    Compressor(threshold_db=-15, ratio=4),
                    Gain(gain_db=2),
                    Reverb(room_size=0.1, dry_level=0.9, wet_level=0.1)
                ])

                # 3. Run processing
                effected = board(audio, samplerate)

                # 4. Save to a virtual file (BytesIO)
                buffer = io.BytesIO()
                with AudioFile(buffer, 'w', samplerate, effected.shape[0]) as f:
                    f.write(effected)
                
                # 5. UI Output
                st.success("Success! Your studio-ready audio is ready.")
                st.write("### Studio Quality")
                st.audio(buffer)
                
                st.download_button(
                    label="Download Result",
                    data=buffer.getvalue(),
                    file_name="studio_voice.wav",
                    mime="audio/wav"
                )

            except Exception as e:
                st.error(f"Error: {e}")
                st.write("Tip: Ensure your file isn't corrupted and is a standard WAV or MP3.")

else:
    st.info("Upload a file above to start the transformation.")
