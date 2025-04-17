
import streamlit as st
import os
import tempfile
import cv2
import numpy as np
from vidstab import VidStab
import subprocess

def stabilize_video(input_path, output_path, level):
    stabilizer = VidStab(kp_method='ORB')
    cap = cv2.VideoCapture(input_path)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    temp_output = output_path.replace(".mp4", "_temp.avi")
    out = cv2.VideoWriter(temp_output, fourcc, fps, (frame_width, frame_height))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        stabilized_frame = stabilizer.stabilize_frame(input_frame=frame, smoothing_window=int(level))
        if stabilized_frame is None:
            stabilized_frame = frame
        out.write(stabilized_frame)

    cap.release()
    out.release()
    crop_black_borders(temp_output, output_path)

def crop_black_borders(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", "cropdetect=24:16:0",
        "-t", "1",
        "-f", "null",
        "-"
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    crop_line = [line for line in result.stderr.splitlines() if "crop=" in line]
    crop_val = crop_line[-1].split("crop=")[-1] if crop_line else "iw:ih"
    subprocess.run([
        "ffmpeg", "-i", input_path,
        "-vf", f"crop={crop_val}",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ], check=True)

st.set_page_config(page_title="AI Video Stabilizer", layout="centered")
st.title("🎥 AI Video Stabilizer med Förhandsvisning")

uploaded_files = st.file_uploader("Ladda upp upp till 5 videor", type=["mp4", "mov", "avi"], accept_multiple_files=True)

level_option = st.selectbox("Välj stabiliseringsnivå", options=["10%", "50%", "90%"])
level_mapping = {"10%": 10, "50%": 30, "90%": 60}
level = level_mapping[level_option]

if uploaded_files:
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
            tmp_file.write(uploaded_file.read())
            input_path = tmp_file.name

        st.video(input_path, format="video/mp4")

        filename = os.path.splitext(uploaded_file.name)[0]
        output_path = f"{filename}_stabilized.mp4"
        stabilize_video(input_path, output_path, level)

        st.success("✅ Stabilisering klar!")
        st.video(output_path, format="video/mp4")
        with open(output_path, "rb") as f:
            st.download_button("Ladda ner stabiliserad video", f, file_name=output_path, mime="video/mp4")
