
import streamlit as st
import tempfile
import os
import subprocess
import datetime
from changelog_updater import update_changelog

st.set_page_config(page_title="AI Video Stabilizer", layout="centered")
st.title("🎥 AI Video Stabilizer")

def convert_to_h264(input_path, output_path, crf=23):
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    subprocess.run(command, check=True)

def stabilize_video(input_path, output_path):
    from vidstab import VidStab
    stabilizer = VidStab()
    stabilizer.stabilize(input_path=input_path, output_path=output_path)

uploaded_file = st.file_uploader("Ladda upp en video", type=["mp4", "mov", "avi"], accept_multiple_files=False)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_input:
        tmp_input.write(uploaded_file.read())
        tmp_input_path = tmp_input.name

    st.video(tmp_input_path)

    stabilized_path = tmp_input_path.replace(".mp4", "_stab.avi")
    final_output_path = tmp_input_path.replace(".mp4", "_final.mp4")

    stabilize_video(tmp_input_path, stabilized_path)
    convert_to_h264(stabilized_path, final_output_path)

    st.success("✅ Färdig!")
    st.video(final_output_path)

    with open(final_output_path, "rb") as f:
        st.download_button("Ladda ner stabiliserad video", f, file_name="stabiliserad_video.mp4")

    update_changelog("1.0.0", "Första version med stöd för stabilisering och H.264-export.")

