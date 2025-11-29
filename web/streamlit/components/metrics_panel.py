import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from web.streamlit.services.metrics_calculator import get_metrics_calculator
from web.streamlit.services.camera_manager import get_camera_manager
from web.streamlit.config.i18n import get_translation
from web.streamlit.config.settings import get_language
from web.streamlit.utils.icons import icon_text
from typing import Optional

def render_metrics_panel(camera_id: Optional[str] = None):
    lang = get_language()
    calculator = get_metrics_calculator()
    metrics = calculator.calculate_metrics(camera_id)
    
    st.header(icon_text("metrics", get_translation("metrics", lang)))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            get_translation("average_confidence", lang),
            f"{metrics['average_confidence']:.3f}"
        )
    
    with col2:
        st.metric(
            get_translation("fps", lang),
            f"{metrics['fps']:.1f}"
        )
    
    with col3:
        st.metric(
            get_translation("track_duration", lang),
            f"{metrics['track_duration']:.1f}s"
        )
    
    with col4:
        st.metric(
            get_translation("unique_objects", lang),
            metrics['unique_objects']
        )
    
    col5, col6 = st.columns(2)
    
    with col5:
        _render_activity_distribution(metrics['activity_distribution'], lang)
    
    with col6:
        _render_detections_chart(metrics['detections_over_time'], lang)

def _render_activity_distribution(distribution: dict, lang: str):
    st.subheader(get_translation("activity_distribution", lang))
    
    labels = [
        get_translation("standing", lang),
        get_translation("moving", lang),
        get_translation("stopped", lang)
    ]
    values = [
        distribution.get("standing", 0),
        distribution.get("moving", 0),
        distribution.get("stopped", 0)
    ]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)
    plt.close(fig)

def _render_detections_chart(time_data: list, lang: str):
    st.subheader(get_translation("detections_over_time", lang))
    
    if not time_data:
        st.info(get_translation("no_data", lang))
        return
    
    hours = [d["hour"] for d in time_data]
    counts = [d["count"] for d in time_data]
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(hours, counts, marker='o', linestyle='-', linewidth=2, markersize=6)
    ax.set_xlabel("Hour")
    ax.set_ylabel("Count")
    ax.grid(True, alpha=0.3)
    ax.set_title(get_translation("detections_over_time", lang))
    st.pyplot(fig)
    plt.close(fig)

def render_metrics_with_camera_selector():
    lang = get_language()
    manager = get_camera_manager()
    cameras = manager.get_all_cameras()
    
    camera_options = [get_translation("all_cameras", lang)] + [cam.name for cam in cameras]
    selected = st.selectbox(
        icon_text("camera", get_translation("camera", lang)),
        camera_options,
        key="metrics_camera_selector"
    )
    
    camera_id = None
    if selected != get_translation("all_cameras", lang):
        selected_camera = next((cam for cam in cameras if cam.name == selected), None)
        if selected_camera:
            camera_id = selected_camera.camera_id
    
    render_metrics_panel(camera_id)

