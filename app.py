import streamlit as st
from df.enhance import enhance, init_df, load_audio, save_audio

# Initialize the model once
model, df_state, _ = init_df()

def enhance_audio(input_path, output_path):
    # Load audio
    audio, _ = load_audio(input_path, sr=df_state.sr())
    # Enhance (Remove noise, reverb, etc.)
    enhanced = enhance(model, df_state, audio)
    # Save processed file
    save_audio(output_path, enhanced, df_state.sr())
