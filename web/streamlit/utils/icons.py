try:
    from streamlit_icons import icon
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False

ICON_MAP = {
    "camera": "📹",
    "people": "👥",
    "train": "🚂",
    "metrics": "📊",
    "logs": "📝",
    "stats": "📈",
    "active": "🟢",
    "inactive": "🔴",
    "settings": "⚙️",
    "search": "🔍",
    "filter": "🔽",
    "refresh": "🔄",
}

def get_icon(name: str) -> str:
    if ICONS_AVAILABLE:
        try:
            icon_name = name.replace("_", "-")
            return icon(icon_name, size=16)
        except:
            return ICON_MAP.get(name, "•")
    return ICON_MAP.get(name, "•")

def icon_text(icon_name: str, text: str) -> str:
    return f"{get_icon(icon_name)} {text}"

