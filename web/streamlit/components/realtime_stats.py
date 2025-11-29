import streamlit as st
import time
from web.streamlit.services.camera_manager import get_camera_manager
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import icon_text

def render_realtime_stats():
    lang = get_language()
    manager = get_camera_manager()
    stats = manager.get_aggregate_stats()
    
    st.header(icon_text("stats", get_translation("realtime_stats", lang)))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            icon_text("people", get_translation("people", lang)),
            stats.get("people", 0)
        )
    
    with col2:
        st.metric(
            icon_text("train", get_translation("trains", lang)),
            stats.get("trains", 0)
        )
    
    with col3:
        st.metric(
            get_translation("total", lang),
            stats.get("total", 0)
        )
    
    with col4:
        st.metric(
            icon_text("camera", get_translation("cameras", lang)),
            stats.get("active_cameras", 0)
        )

def render_realtime_stats_auto_refresh(interval: int = 5):
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            render_realtime_stats()
        time.sleep(interval)

