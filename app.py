import streamlit as st
import io

# --- PYTHON 3.13/3.14 COMPATIBILITY HOTFIX ---
try:
    import audioop
except ImportError:
    import audioop_lpm as audioop
    import sys
    sys.modules['audioop'] = audioop
# ----------------------------------------------

from pydub import AudioSegment
from pydub.effects import normalize

st.set_page_config(page_title="Studio Voice AI", page_icon="🎙️")

st.title("🎙️ AI Studio Voice Enhancer")
st.caption("Fixed for Python 3.13+ compatibility")

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
