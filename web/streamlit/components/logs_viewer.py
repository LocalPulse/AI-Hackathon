import streamlit as st
import pandas as pd
from web.streamlit.services.data_service import get_data_service
from web.streamlit.services.camera_manager import get_camera_manager
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import icon_text
from typing import Optional

def render_logs_viewer():
    lang = get_language()
    data_service = get_data_service()
    camera_manager = get_camera_manager()
    
    st.header(icon_text("logs", get_translation("logs", lang)))
    
    cameras = camera_manager.get_all_cameras()
    camera_options = [get_translation("all_cameras", lang)] + [cam.name for cam in cameras]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_camera = st.selectbox(
            icon_text("camera", get_translation("camera", lang)),
            camera_options,
            key="logs_camera_selector"
        )
    
    with col2:
        class_filter = st.selectbox(
            get_translation("filter_by_class", lang),
            [None, "person", "train"],
            key="logs_class_filter"
        )
    
    with col3:
        activity_filter = st.selectbox(
            get_translation("filter_by_activity", lang),
            [None, "standing", "moving", "stopped"],
            key="logs_activity_filter"
        )
    
    camera_id = None
    if selected_camera != get_translation("all_cameras", lang):
        selected_cam = next((cam for cam in cameras if cam.name == selected_camera), None)
        if selected_cam:
            camera_id = selected_cam.camera_id
    
    page_size = st.slider("Items per page", 10, 100, 50, key="logs_page_size")
    
    if "log_page" not in st.session_state:
        st.session_state.log_page = 0
    
    total_count = data_service.get_log_count(
        class_filter=class_filter,
        activity_filter=activity_filter,
        camera_id=camera_id
    )
    
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
    
    col4, col5, col6 = st.columns([1, 2, 1])
    
    with col4:
        prev_text = get_translation("previous", lang)
        if st.button(f"← {prev_text}", disabled=st.session_state.log_page == 0, key="logs_prev_button"):
            st.session_state.log_page = max(0, st.session_state.log_page - 1)
            st.rerun()
    
    with col5:
        st.caption(f"Page {st.session_state.log_page + 1} of {total_pages} ({total_count} total)")
    
    with col6:
        next_text = get_translation("next", lang)
        if st.button(f"{next_text} →", disabled=st.session_state.log_page >= total_pages - 1, key="logs_next_button"):
            st.session_state.log_page = min(total_pages - 1, st.session_state.log_page + 1)
            st.rerun()
    
    offset = st.session_state.log_page * page_size
    
    logs = data_service.get_logs(
        limit=page_size,
        offset=offset,
        class_filter=class_filter,
        activity_filter=activity_filter,
        camera_id=camera_id
    )
    
    if not logs:
        st.info(get_translation("no_data", lang))
        return
    
    df_data = []
    for log in logs:
        camera_name = "N/A"
        if log.camera_id:
            cam = camera_manager.get_camera(log.camera_id)
            if cam:
                camera_name = cam.name
        
        df_data.append({
            get_translation("timestamp", lang): log.timestamp,
            get_translation("camera", lang): camera_name,
            get_translation("track_id", lang): log.track_id,
            get_translation("class", lang): log.class_name,
            get_translation("activity", lang): log.activity,
            get_translation("confidence", lang): f"{log.confidence:.2f}"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, width='stretch', hide_index=True)

