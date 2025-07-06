import streamlit as st
import os
import uuid
import shutil
import ffmpeg

TEMP_DIR = "temp_clips"
os.makedirs(TEMP_DIR, exist_ok=True)

def split_video_ffmpeg(file_path, segment_duration):
    try:
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        clips = []

        for i in range(0, int(duration), segment_duration):
            start = i
            end = min(i + segment_duration, int(duration))
            output_path = os.path.join(TEMP_DIR, f"clip_{start}_{end}.mp4")

            (
                ffmpeg
                .input(file_path, ss=start, t=(end - start))
                .output(output_path, c='copy')
                .run(quiet=True, overwrite_output=True)
            )
            clips.append(output_path)

        return clips

    except Exception as e:
        st.error(f"🚨 ffmpeg error: {e}")
        return []

def clean_temp_dir():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

# Setup
st.set_page_config(page_title="Fast Video Splitter", layout="centered")
st.title("🎬 Smart Video Splitter Bot (Ultra Fast ⚡)")
st.caption("📁 Upload a video (max 2GB) and split it into smaller clips instantly.")

# Inputs
uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
split_minutes = st.number_input("Split duration (in minutes)", min_value=1, step=1)

if 'clip_paths' not in st.session_state:
    st.session_state.clip_paths = []

if uploaded_file and split_minutes:
    unique_filename = f"{uuid.uuid4()}.mp4"
    input_path = os.path.join(TEMP_DIR, unique_filename)

    with st.spinner("Saving uploaded video..."):
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())
    st.success("✅ Video uploaded successfully!")

    if st.button("🔪 Split Video"):
        st.info("Splitting video... please wait ⏳")
        clip_paths = split_video_ffmpeg(input_path, split_minutes * 60)
        if clip_paths:
            st.session_state.clip_paths = clip_paths
            st.success(f"✅ Done! {len(clip_paths)} clips generated.")
        else:
            st.error("❌ No clips were generated.")

# Show download buttons
if st.session_state.clip_paths:
    st.subheader("📥 Download your split clips:")
    for clip_path in st.session_state.clip_paths:
        st.video(clip_path)
        try:
            with open(clip_path, "rb") as f:
                btn_key = f"download_{os.path.basename(clip_path)}"
                st.download_button(
                    label=f"Download {os.path.basename(clip_path)}",
                    data=f.read(),  # 🔁 Read only during button render
                    file_name=os.path.basename(clip_path),
                    mime="video/mp4",
                    key=btn_key
                )
        except Exception as e:
            st.error(f"Failed to load: {clip_path}\n{e}")

# Optional cleanup
if st.button("🗑️ Clear All Clips"):
    clean_temp_dir()
    st.session_state.clip_paths = []
    st.success("✅ All clips cleared.")
