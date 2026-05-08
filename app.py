import streamlit as st
from pydub import AudioSegment
from pydub.effects import normalize
import io

st.set_page_config(page_title="Stable Voice AI", page_icon="🎙️")

st.title("🎙️ AI Studio Voice Enhancer")
st.info("Using Stable Engine (No Install Errors)")

uploaded_file = st.file_uploader("Upload Audio", type=['wav', 'mp3'])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')
    
    if st.button("✨ Enhance Voice"):
        with st.spinner("Processing..."):
            try:
                # 1. Load the audio
                audio = AudioSegment.from_file(uploaded_file)

                # 2. STUDIO PROCESSING
                # Normalize: Brings volume to a professional level
                enhanced = normalize(audio)
                
                # High Pass Filter: Removes low-end background hum (80Hz)
                enhanced = enhanced.high_pass_filter(80)
                
                # Low Pass Filter: Smooths out harsh high-end noise
                enhanced = enhanced.low_pass_filter(8000)

                # 3. Export to buffer
                buffer = io.BytesIO()
                enhanced.export(buffer, format="wav")
                
                st.success("Enhancement Complete!")
                st.audio(buffer.getvalue(), format='audio/wav')
                
                st.download_button(
                    label="Download Studio Version",
                    data=buffer.getvalue(),
                    file_name="enhanced_voice.wav",
                    mime="audio/wav"
                )

            except Exception as e:
                st.error(f"Error: {e}")
                st.info("Make sure ffmpeg is in your packages.txt file.")
