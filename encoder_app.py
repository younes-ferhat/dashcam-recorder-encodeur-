import streamlit as st
import cv2
import time
import os
import hashlib
from supabase import create_client
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

# --- CONFIGURATION ---
URL = "https://iiqxkqyxcxehrxujkbfs.supabase.co"
KEY = "TON_CLE_SUPABASE"

DUREE_SEGMENT = 10
FPS = 20
FRAMES_PAR_SEGMENT = DUREE_SEGMENT * FPS

st.set_page_config(page_title="DashCam Security Pro", page_icon="🚗", layout="wide")

# --- INITIALISATION SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(URL, KEY)
    except:
        return None

supabase = init_supabase()

os.makedirs("buffer_local", exist_ok=True)
os.makedirs("temp_videos", exist_ok=True)

# --- WEBCAM VIA NAVIGATEUR ---
class VideoProcessor(VideoTransformerBase):
    def __init__(self):
        self.last_frame = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        self.last_frame = img
        return img

# --- OUTILS ---
def calculer_hash(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()

def envoyer_segment(path, nom, signature):
    if not supabase: return False
    try:
        with open(path, "rb") as f:
            supabase.storage.from_("video-frames").upload(nom, f, file_options={"content-type": "video/mp4"})
        supabase.table("video_frames").insert({"hash": nom, "storage_url": signature}).execute()
        return True
    except:
        return False

# --- UI ---
st.title("🚗 DashCam Security Pro — Cloud")

st.markdown("### 🎥 Caméra (via navigateur)")

ctx = webrtc_streamer(
    key="dashcam",
    video_processor_factory=VideoProcessor,
    media_stream_constraints={"video": True, "audio": False},
    async_processing=True,
)

if "recording" not in st.session_state:
    st.session_state.recording = False

if st.button("🔴 Démarrer / Arrêter"):
    st.session_state.recording = not st.session_state.recording

if ctx.video_processor:
    vp = ctx.video_processor

    if "buffer" not in st.session_state:
        st.session_state.buffer = []

    if st.session_state.recording and vp.last_frame is not None:
        st.session_state.buffer.append(vp.last_frame)

    if len(st.session_state.buffer) >= FRAMES_PAR_SEGMENT:
        frames = st.session_state.buffer.copy()
        st.session_state.buffer.clear()

        h, w, _ = frames[0].shape
        nom = f"segment_{int(time.time())}.mp4"
        path = os.path.join("temp_videos", nom)

        out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (w, h))
        for f in frames:
            out.write(f)
        out.release()

        hash_sign = calculer_hash(path)
        succes = envoyer_segment(path, nom, hash_sign)

        if succes:
            st.success(f"✅ Segment envoyé : {nom}")
            os.remove(path)
        else:
            st.warning(f"⚠️ Cloud indisponible — stocké localement")
            os.rename(path, os.path.join("buffer_local", nom))
