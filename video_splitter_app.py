import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
import os
import uuid

# Directory to store temporary files
TEMP_DIR = "temp_clips"
os.makedirs(TEMP_DIR, exist_ok=True)

def split_video(file_path, segment_duration):
    clip = VideoFileClip(file_path)
    video_duration = int(clip.duration)
    clips = []

    for start in range(0, video_duration, segment_duration):
        end = min(start + segment_duration, video_duration)
        subclipped = clip.subclipped(start, end)

        filename = f"{TEMP_DIR}/clip_{start}_{end}.mp4"
        subclipped.write_videofile(filename, codec="libx264", audio_codec='aac')
        clips.append(filename)
    
    return clips

st.title("🎬 Smart Video Splitter Bot")
st.write("Upload any video and split it into smaller clips automatically based on your chosen duration.")

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
split_minutes = st.number_input("Split duration (in minutes)", min_value=1, step=1)

if uploaded_file and split_minutes:
    with st.spinner("Saving uploaded video..."):
        unique_filename = f"{uuid.uuid4()}.mp4"
        input_path = os.path.join(TEMP_DIR, unique_filename)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())
    
    st.success("Video uploaded successfully!")

    if st.button("🔪 Split Video"):
        st.info("Splitting video... please wait.")
        clips = split_video(input_path, split_minutes * 60)

        st.success(f"Done! Generated {len(clips)} clips.")
        for clip_path in clips:
            st.video(clip_path)
            with open(clip_path, "rb") as f:
                st.download_button(label=f"Download {os.path.basename(clip_path)}", data=f, file_name=os.path.basename(clip_path))

# Clean up temp folder if needed (optional)
