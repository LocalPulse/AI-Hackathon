import streamlit as st
from typing import Literal

Theme = Literal["light", "dark"]
Language = Literal["en", "ru"]

def init_session_state():
    st.session_state.theme = "dark"
    if "language" not in st.session_state:
        st.session_state.language = "en"

def get_theme() -> Theme:
    init_session_state()
    return st.session_state.theme

def set_theme(theme: Theme):
    st.session_state.theme = theme

def get_language() -> Language:
    init_session_state()
    return st.session_state.language

def set_language(lang: Language):
    st.session_state.language = lang

