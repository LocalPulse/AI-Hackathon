import streamlit as st
import pandas as pd
import time
from web.streamlit.services.data_service import get_data_service
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import icon_text
from typing import Optional

def render_logs_viewer():
    lang = get_language()
    data_service = get_data_service()
    
    st.header(icon_text("logs", get_translation("logs", lang)))
    
    # Auto-refresh toggle
    col_refresh1, col_refresh2 = st.columns([1, 3])
    with col_refresh1:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, key="auto_refresh_logs")
    with col_refresh2:
        if auto_refresh:
            st.caption("Updates every 2 seconds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        class_filter = st.selectbox(
            get_translation("filter_by_class", lang),
            [None, "person", "train"],
            key="logs_class_filter"
        )
    
    with col2:
        activity_filter = st.selectbox(
            get_translation("filter_by_activity", lang),
            [None, "standing", "moving", "stopped"],
            key="logs_activity_filter"
        )
    
    page_size = st.slider("Items per page", 10, 100, 50, key="logs_page_size")
    
    if "log_page" not in st.session_state:
        st.session_state.log_page = 0
    
    # Create placeholder for dynamic content
    placeholder = st.empty()
    
    # Auto-refresh loop
    while auto_refresh:
        with placeholder.container():
            _render_logs_content(data_service, lang, class_filter, activity_filter, page_size)
        
        time.sleep(2)  # Refresh every 2 seconds
        st.rerun()
    
    # If auto-refresh is off, render once
    with placeholder.container():
        _render_logs_content(data_service, lang, class_filter, activity_filter, page_size)


def _render_logs_content(data_service, lang, class_filter, activity_filter, page_size):
    """Render the logs content (separated for reusability)."""
    total_count = data_service.get_log_count(
        class_filter=class_filter,
        activity_filter=activity_filter
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
        activity_filter=activity_filter
    )
    
    if not logs:
        st.info(get_translation("no_data", lang))
        return
    
    df_data = []
    for log in logs:
        df_data.append({
            get_translation("timestamp", lang): log.timestamp,
            get_translation("track_id", lang): log.track_id,
            get_translation("class", lang): log.class_name,
            get_translation("activity", lang): log.activity,
            get_translation("confidence", lang): f"{log.confidence:.2f}"
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

