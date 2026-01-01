import streamlit as st
import cv2
import time
import os
import hashlib
from supabase import create_client
from datetime import datetime

# --- CONFIGURATION ---
URL = "https://iiqxkqyxcxehrxujkbfs.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlpcXhrcXl4Y3hlaHJ4dWprYmZzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY1NzE3NTEsImV4cCI6MjA4MjE0Nzc1MX0.SuN11uwMpzWNvmZAGcK2BGf7DWsKi5o2O1rkbJuWXnE"

DUREE_SEGMENT = 10
FPS = 20
FRAMES_PAR_SEGMENT = DUREE_SEGMENT * FPS

st.set_page_config(page_title="DashCam Security Pro", page_icon="🚗", layout="wide")

# --- CSS MODERNE ET SOPHISTIQUÉ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Header personnalisé */
    .main-header {
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: rgba(255,255,255,0.7);
        font-size: 1.1rem;
        font-weight: 300;
    }
    
    /* Dot animation améliorée */
    .rec-dot {
        height: 18px;
        width: 18px;
        background: linear-gradient(135deg, #ff0844 0%, #ff4b6e 100%);
        border-radius: 50%;
        display: inline-block;
        animation: pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 20px rgba(255, 8, 68, 0.8);
        margin-right: 10px;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.7; }
    }
    
    /* Cards avec effet glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        margin-bottom: 1rem;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(102, 126, 234, 0.6);
    }
    
    /* Métriques stylisées */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    div[data-testid="stMetricLabel"] {
        color: rgba(255,255,255,0.7);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Video container */
    .video-container {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 1rem;
        border: 2px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Logs stylisés */
    .log-container {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-height: 500px;
        overflow-y: auto;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        margin-right: 0.5rem;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    
    /* Scrollbar personnalisée */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Divider stylisé */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- INITIALISATION SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        return create_client(URL, KEY)
    except Exception as e:
        st.error(f"❌ Erreur de connexion Supabase: {e}")
        return None

supabase = init_supabase()

if not os.path.exists("buffer_local"): os.makedirs("buffer_local")
if not os.path.exists("temp_videos"): os.makedirs("temp_videos")

# --- FONCTIONS MÉTIER ---
def calculer_hash(path):
    sha256 = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def envoyer_segment(chemin, nom, signature):
    if not supabase: return False
    try:
        with open(chemin, 'rb') as f:
            supabase.storage.from_("video-frames").upload(nom, f, file_options={"content-type": "video/mp4"})
        supabase.table("video_frames").insert({"hash": nom, "storage_url": signature}).execute()
        return True
    except Exception as e:
        return False

def maintenance_nettoyage():
    if not supabase: return None
    try:
        logs = supabase.table("video_frames").select("*").order("created_at", desc=False).execute().data
        while len(logs) > 5:
            old = logs.pop(0)
            try:
                supabase.storage.from_("video-frames").remove([old['hash']])
                supabase.table("video_frames").delete().eq("id", old['id']).execute()
            except:
                pass
            return f"♻️ {old['hash']} supprimé"
    except:
        pass
    return None

def synchroniser_buffer(log_container):
    fichiers_buffer = os.listdir("buffer_local")
    if fichiers_buffer:
        for f_buf in fichiers_buffer:
            p_buf = os.path.join("buffer_local", f_buf)
            h_buf = calculer_hash(p_buf)
            
            if envoyer_segment(p_buf, f_buf, h_buf):
                os.remove(p_buf)
                log_container.success(f"🔄 Buffer récupéré : {f_buf}")
                time.sleep(0.5)

# --- HEADER SOPHISTIQUÉ ---
st.markdown("""
<div class="main-header">
    <div class="main-title">🚗 DashCam Security Pro</div>
    <div class="subtitle">Système d'enregistrement intelligent avec blockchain intégrée</div>
</div>
""", unsafe_allow_html=True)

# --- ÉTAT DU SYSTÈME ---
col_status1, col_status2, col_status3, col_status4 = st.columns(4)

with col_status1:
    status_cloud = "🟢 En ligne" if supabase else "🔴 Hors ligne"
    st.metric("État Cloud", status_cloud, delta="OK" if supabase else "Erreur")

with col_status2:
    nb_buffer = len(os.listdir("buffer_local"))
    st.metric("Buffer Local", nb_buffer, delta="vidéos", delta_color="inverse")

with col_status3:
    if supabase:
        try:
            total = len(supabase.table("video_frames").select("*").execute().data)
            st.metric("Preuves Cloud", total, delta="segments")
        except:
            st.metric("Preuves Cloud", "N/A")
    else:
        st.metric("Preuves Cloud", "N/A")

with col_status4:
    now = datetime.now().strftime("%H:%M:%S")
    st.metric("Horloge Système", now)

st.markdown("---")

# --- CONTRÔLES D'ENREGISTREMENT ---
if "recording" not in st.session_state:
    st.session_state.recording = False

col_control1, col_control2, col_control3 = st.columns([2, 1, 1])

with col_control1:
    if not st.session_state.recording:
        if st.button("🔴 DÉMARRER L'ENREGISTREMENT", type="primary", use_container_width=True):
            st.session_state.recording = True
            st.rerun()
    else:
        if st.button("⏹️ ARRÊTER L'ENREGISTREMENT", use_container_width=True):
            st.session_state.recording = False
            st.rerun()

with col_control2:
    st.markdown(f"""
    <div class="status-badge {'badge-success' if st.session_state.recording else 'badge-warning'}">
        {'🎥 ACTIF' if st.session_state.recording else '⏸️ VEILLE'}
    </div>
    """, unsafe_allow_html=True)

with col_control3:
    if st.button("🔄 Synchroniser Buffer", use_container_width=True):
        with st.spinner("Synchronisation..."):
            synchroniser_buffer(st)
        st.rerun()

st.markdown("---")

# --- INTERFACE PRINCIPALE ---
col_video, col_logs = st.columns([3, 2])

if st.session_state.recording:
    with col_video:
        st.markdown('### <span class="rec-dot"></span>Flux Caméra en Direct', unsafe_allow_html=True)
        video_placeholder = st.empty()
        
    with col_logs:
        st.markdown("### 📡 Journal d'Activité")
        log_actuel = st.empty()
        log_history = st.container()

    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        st.error("❌ Impossible d'accéder à la caméra")
        st.session_state.recording = False
        st.stop()
        
    largeur = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hauteur = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    compteur = 1
    
    try:
        while st.session_state.recording:
            timestamp = str(int(time.time()))
            nom_fichier = f"video_{timestamp}.mp4"
            chemin_temp = os.path.join("temp_videos", nom_fichier)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(chemin_temp, fourcc, FPS, (largeur, hauteur))
            
            for i in range(FRAMES_PAR_SEGMENT):
                ret, frame = cap.read()
                if not ret: break
                
                out.write(frame)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
                
                if i % 20 == 0:
                    progress = (i / FRAMES_PAR_SEGMENT) * 100
                    log_actuel.info(f"🎬 Segment {compteur} : {progress:.0f}% ({i}/{FRAMES_PAR_SEGMENT} frames)")

            out.release()
            
            hash_sign = calculer_hash(chemin_temp)
            log_actuel.info(f"🔐 Hash: {hash_sign[:16]}... | Transmission...")
            
            succes = envoyer_segment(chemin_temp, nom_fichier, hash_sign)
            
            with log_history:
                if succes:
                    st.success(f"✅ Segment {compteur} certifié et envoyé au cloud")
                    synchroniser_buffer(st)
                    msg_clean = maintenance_nettoyage()
                    if msg_clean:
                        st.caption(msg_clean)
                else:
                    dest = os.path.join("buffer_local", nom_fichier)
                    if os.path.exists(chemin_temp):
                        if os.path.exists(dest): os.remove(dest)
                        os.rename(chemin_temp, dest)
                    st.warning(f"⚠️ Segment {compteur} sauvegardé localement (cloud indisponible)")
            
            if os.path.exists(chemin_temp):
                os.remove(chemin_temp)
            
            compteur += 1

    except Exception as e:
        st.error(f"❌ Erreur critique : {e}")
    finally:
        cap.release()
        
else:
    with col_video:
        st.markdown("### 📹 Prévisualisation Caméra")
        st.image("https://placehold.co/800x600/1a1a2e/667eea?text=Camera+en+Veille", 
                 use_container_width=True)
        st.info("💡 Cliquez sur 'DÉMARRER L'ENREGISTREMENT' pour activer la surveillance")
    
    with col_logs:
        st.markdown("### 📊 Statistiques Système")
        st.markdown("""
        <div class="glass-card">
            <h4>Dernière Session</h4>
            <p>Aucune session active</p>
        </div>
        """, unsafe_allow_html=True)
        
        if supabase:
            try:
                recent = supabase.table("video_frames").select("*").order("created_at", desc=True).limit(5).execute().data
                if recent:
                    st.markdown("#### 🕐 Derniers Segments")
                    for r in recent:
                        st.caption(f"• {r['hash']} - {r['created_at'][:19]}")
            except:
                pass