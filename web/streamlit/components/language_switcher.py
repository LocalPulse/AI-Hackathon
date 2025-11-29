import streamlit as st
from web.streamlit.config.settings import get_theme, set_theme, get_language, set_language
from web.streamlit.config.i18n import get_translation

def render_theme_switcher():
    lang = get_language()
    current_theme = get_theme()
    
    st.selectbox(
        get_translation("theme", lang),
        ["light", "dark"],
        index=0 if current_theme == "light" else 1,
        format_func=lambda x: get_translation(x, lang),
        key="theme_selector",
        on_change=_on_theme_change
    )

def render_language_switcher():
    lang = get_language()
    
    st.selectbox(
        get_translation("language", lang),
        ["en", "ru"],
        index=0 if lang == "en" else 1,
        format_func=lambda x: "English" if x == "en" else "Русский",
        key="language_selector",
        on_change=_on_language_change
    )

def _on_theme_change():
    new_theme = st.session_state.theme_selector
    set_theme(new_theme)

def _on_language_change():
    new_lang = st.session_state.language_selector
    set_language(new_lang)

