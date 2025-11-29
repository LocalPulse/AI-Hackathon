import streamlit as st
import time
from web.streamlit.services.camera_manager import get_camera_manager
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import icon_text

# Import shared state for real-time data
try:
    from web.api.utils.shared_state import get_shared_state
    SHARED_STATE_AVAILABLE = True
except ImportError:
    SHARED_STATE_AVAILABLE = False

def render_realtime_stats():
    """Render real-time statistics with auto-refresh."""
    lang = get_language()
    
    st.header(icon_text("stats", get_translation("realtime_stats", lang)))
    
    # Auto-refresh toggle
    col_refresh1, col_refresh2 = st.columns([1, 3])
    with col_refresh1:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, key="auto_refresh_stats")
    with col_refresh2:
        if auto_refresh:
            st.caption("Updates every 1 second")
    
    # Create placeholder for dynamic content
    placeholder = st.empty()
    
    # Auto-refresh loop
    while auto_refresh:
        with placeholder.container():
            _render_stats_content(lang)
        
        time.sleep(1)  # Refresh every 1 second
        st.rerun()
    
    # If auto-refresh is off, render once
    with placeholder.container():
        _render_stats_content(lang)


def _render_stats_content(lang: str):
    """Render the actual statistics content."""
    # Get real-time stats from shared state (currently active tracks)
    if SHARED_STATE_AVAILABLE:
        shared_state = get_shared_state()
        realtime_stats = shared_state.get_stats()
        people_now = realtime_stats.get('person', 0)
        trains_now = realtime_stats.get('train', 0)
        total_now = realtime_stats.get('total', 0)
    else:
        people_now = 0
        trains_now = 0
        total_now = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            icon_text("people", get_translation("people", lang) + " (Now)"),
            people_now,
            help="Currently visible people in video"
        )
    
    with col2:
        st.metric(
            icon_text("train", get_translation("trains", lang) + " (Now)"),
            trains_now,
            help="Currently visible trains in video"
        )
    
    with col3:
        st.metric(
            get_translation("total", lang) + " (Now)",
            total_now,
            help="Total currently visible objects"
        )
    
    with col4:
        # Show status
        status = "🟢 Active" if SHARED_STATE_AVAILABLE and total_now > 0 else "⚪ Idle"
        st.metric(
            "Status",
            status,
            help="Video processing status"
        )


def render_realtime_stats_auto_refresh(interval: int = 5):
    """Legacy function for compatibility."""
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            render_realtime_stats()
        time.sleep(interval)

