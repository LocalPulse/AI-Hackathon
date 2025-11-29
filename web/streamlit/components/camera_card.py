import streamlit as st
from web.streamlit.services.camera_manager import get_camera_manager
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import get_icon, icon_text

def render_camera_card(camera_id: str):
    lang = get_language()
    manager = get_camera_manager()
    camera = manager.get_camera(camera_id)
    
    if not camera:
        st.error(get_translation("no_data", lang))
        return
    
    stats = manager.get_camera_stats(camera_id)
    status_icon = get_icon("active") if camera.status == "active" else get_icon("inactive")
    status_text = get_translation("active", lang) if camera.status == "active" else get_translation("inactive", lang)
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"### {get_icon('camera')} {camera.name}")
            st.caption(f"{status_icon} {status_text}")
        
        with col2:
            st.metric(
                get_translation("total", lang),
                stats.get("total", 0)
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.metric(
                icon_text("people", get_translation("people", lang)),
                stats.get("people", 0)
            )
        
        with col4:
            st.metric(
                icon_text("train", get_translation("trains", lang)),
                stats.get("trains", 0)
            )

def render_cameras_grid():
    lang = get_language()
    manager = get_camera_manager()
    cameras = manager.get_all_cameras()
    
    if not cameras:
        st.info(get_translation("no_data", lang))
        return
    
    cols = st.columns(min(len(cameras), 3))
    
    for idx, camera in enumerate(cameras):
        with cols[idx % len(cols)]:
            render_camera_card(camera.camera_id)

