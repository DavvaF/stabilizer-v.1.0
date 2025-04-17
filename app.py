
import streamlit as st
import tempfile
import os
import subprocess
import cv2
import time
from vidstab import VidStab

def stabilize_video(input_path, output_path, level):
    stab = VidStab(kalman_gain=0.2 * level)  # Dynamiskt justerad stabilisering
    stab.stabilize(input_path=input_path, output_path=output_path, border_size=20)

def crop_black_bars(input_path, output_path):
    cropdetect_cmd = [
        "ffmpeg", "-i", input_path, "-vf", "cropdetect=24:16:0", "-t", "1", "-f", "null", "-"
    ]
    result = subprocess.run(cropdetect_cmd, stderr=subprocess.PIPE, text=True)
    crop_lines = [line for line in result.stderr.split("\n") if "crop=" in line]
    if crop_lines:
        crop_values = crop_lines[-1].split("crop=")[-1]
        crop_cmd = [
            "ffmpeg", "-i", input_path, "-vf", f"crop={crop_values}", "-c:a", "copy", output_path
        ]
        subprocess.run(crop_cmd, check=True)

def convert_to_h264(input_path, output_path):
    command = [
        "ffmpeg", "-i", input_path,
        "-vcodec", "libx264", "-preset", "fast", "-crf", "23",
        "-acodec", "aac", "-b:a", "128k",
        output_path
    ]
    subprocess.run(command, check=True)

st.set_page_config(page_title="AI Video Stabilizer", layout="centered")
st.title("🎥 AI Video Stabilizer")

uploaded_file = st.file_uploader("Ladda upp en video", type=["mp4", "mov", "avi"])
stabilization_level = st.slider("Stabiliseringsnivå (%)", 10, 90, 50, step=10)

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_input:
        temp_input.write(uploaded_file.read())
        input_path = temp_input.name

    st.video(input_path, format="video/mp4", start_time=0)

    if st.button("Stabilisera video"):
        start = time.time()
        with st.spinner("Stabiliserar..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as temp_stab:
                stabilized_path = temp_stab.name
            stabilize_video(input_path, stabilized_path, stabilization_level / 100)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_cropped:
                cropped_path = temp_cropped.name
            crop_black_bars(stabilized_path, cropped_path)

            final_output_path = cropped_path.replace(".mp4", "_final.mp4")
            convert_to_h264(cropped_path, final_output_path)

        total_time = int(time.time() - start)
        st.success(f"✅ Klar! Bearbetningstid: {total_time} sekunder")

        st.subheader("🎬 Förhandsgranskning av redigerad video")
        st.video(final_output_path)

        with open(final_output_path, "rb") as f:
            st.download_button("📥 Ladda ner stabiliserad video", f, file_name="stabiliserad_video.mp4")
