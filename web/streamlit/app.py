import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web.streamlit.config.settings import init_session_state, get_theme, get_language
from web.streamlit.config.i18n import get_translation
from web.streamlit.components.language_switcher import render_language_switcher
from web.streamlit.components.realtime_stats import render_realtime_stats
from web.streamlit.components.camera_card import render_cameras_grid
from web.streamlit.components.metrics_panel import render_metrics_with_camera_selector
from web.streamlit.components.logs_viewer import render_logs_viewer
from web.streamlit.utils.icons import get_icon

def main():
    init_session_state()
    
    theme = get_theme()
    lang = get_language()
    
    st.set_page_config(
        page_title=get_translation("app_title", lang),
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    _apply_custom_css(theme)
    
    col_settings1, col_settings2 = st.columns([1, 11])
    
    with col_settings1:
        render_language_switcher()
    
    st.divider()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        get_icon("stats") + " " + get_translation("realtime_stats", lang),
        get_icon("camera") + " " + get_translation("cameras", lang),
        get_icon("metrics") + " " + get_translation("metrics", lang),
        get_icon("logs") + " " + get_translation("logs", lang),
    ])
    
    with tab1:
        render_realtime_stats()
    
    with tab2:
        render_cameras_grid()
    
    with tab3:
        render_metrics_with_camera_selector()
    
    with tab4:
        render_logs_viewer()

def _apply_custom_css(theme: str):
    css_path = Path(__file__).parent / "styles.css"
    
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        
        bg_color = "#0E1117"
        text_color = "#FAFAFA"
        sidebar_bg = "#1E1E1E"
        sidebar_text = "#FFFFFF"
        sidebar_button_bg = "#2A2A2A"
        sidebar_button_hover = "#3A3A3A"
        sidebar_input_bg = "#2A2A2A"
        sidebar_input_text = "#FFFFFF"
        sidebar_border = "rgba(255, 255, 255, 0.2)"
        sidebar_border_hover = "rgba(255, 255, 255, 0.4)"
        border_color = "rgba(255, 255, 255, 0.1)"
        border_hover = "rgba(255, 255, 255, 0.3)"
        popover_hover = "rgba(255, 255, 255, 0.1)"
        metric_bg = "rgba(255, 255, 255, 0.05)"
        anchor_text = "#FAFAFA"
        
        font = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
        
        css = css.replace("__BG__", bg_color)
        css = css.replace("__TEXT__", text_color)
        css = css.replace("__FONT__", font)
        css = css.replace("__SIDEBAR_BG__", sidebar_bg)
        css = css.replace("__SIDEBAR_TEXT__", sidebar_text)
        css = css.replace("__SIDEBAR_BUTTON_BG__", sidebar_button_bg)
        css = css.replace("__SIDEBAR_BUTTON_HOVER__", sidebar_button_hover)
        css = css.replace("__SIDEBAR_INPUT_BG__", sidebar_input_bg)
        css = css.replace("__SIDEBAR_INPUT_TEXT__", sidebar_input_text)
        css = css.replace("__SIDEBAR_BORDER__", sidebar_border)
        css = css.replace("__SIDEBAR_BORDER_HOVER__", sidebar_border_hover)
        css = css.replace("__BORDER_COLOR__", border_color)
        css = css.replace("__BORDER_HOVER__", border_hover)
        css = css.replace("__POPOVER_HOVER__", popover_hover)
        css = css.replace("__METRIC_BG__", metric_bg)
        css = css.replace("__ANCHOR_TEXT__", anchor_text)
        
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

