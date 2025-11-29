import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
try:
    from sqlalchemy import create_engine
except Exception:
    create_engine = None
try:
    # optional helper for automatic page refresh
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None
import numpy as np
from typing import Optional
from pathlib import Path


def inject_css(font_family: str, bg_color: str, text_color: str) -> None:
    """Apply CSS theme to Streamlit app"""
    css_path = Path(__file__).parent / 'styles.css'
    try:
        if css_path.exists():
            css = css_path.read_text(encoding='utf-8')
            css = css.replace('__FONT__', font_family).replace('__BG__', bg_color).replace('__TEXT__', text_color)
            
            extra_css = f"""
            * {{ color: {text_color} !important; }}
            body {{ color: {text_color} !important; }}
            body * {{ color: {text_color} !important; }}
            .stApp {{ color: {text_color} !important; }}
            .stApp * {{ color: {text_color} !important; }}
            p {{ color: {text_color} !important; }}
            span {{ color: {text_color} !important; }}
            div {{ color: {text_color} !important; }}
            label {{ color: {text_color} !important; }}
            h1 {{ color: {text_color} !important; }}
            h2 {{ color: {text_color} !important; }}
            h3 {{ color: {text_color} !important; }}
            h4 {{ color: {text_color} !important; }}
            h5 {{ color: {text_color} !important; }}
            h6 {{ color: {text_color} !important; }}
            button {{ color: {text_color} !important; }}
            input {{ color: {text_color} !important; }}
            select {{ color: {text_color} !important; }}
            textarea {{ color: {text_color} !important; }}
            option {{ color: {text_color} !important; }}
            [style] {{ color: {text_color} !important; }}
            """
            
            st.markdown(f"<style>{css}{extra_css}</style>", unsafe_allow_html=True)
            return
    except Exception as e:
        print(f"CSS load error: {e}")

    fallback_css = f"""
    <style>
    * {{ color: {text_color} !important; }}
    body * {{ color: {text_color} !important; }}
    .stApp * {{ color: {text_color} !important; }}
    p, span, div, label, h1, h2, h3, h4, h5, h6, button, input, select, textarea, option {{ 
      color: {text_color} !important; 
    }}
    [style] {{ color: {text_color} !important; }}
    </style>
    """
    st.markdown(fallback_css, unsafe_allow_html=True)


class SimpleDashboard:
    def __init__(self, auto_file: Optional[str] = None, db_conn: Optional[str] = None, db_table: Optional[str] = None, db_is_query: bool = False):
        st.set_page_config(page_title="Simple Dashboard", layout="wide")
        self.data: Optional[pd.DataFrame] = None
        self.auto_file = auto_file
        self.theme = "Dark"
        # DB connection provided via CLI or integration; UI SQL upload removed
        self.db_conn = db_conn
        self.db_table = db_table
        self.db_is_query = db_is_query

    def load_data(self, uploaded_file) -> Optional[pd.DataFrame]:
        if uploaded_file is None:
            return None
        try:
            if isinstance(uploaded_file, str):
                path = uploaded_file
                if path.endswith('.csv'):
                    return pd.read_csv(path)
                else:
                    return pd.read_excel(path)

            name = uploaded_file.name
            if name.endswith('.csv'):
                return pd.read_csv(uploaded_file)
            return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Ошибка при загрузке данных: {e}")
            return None

    def fetch_data_from_sql(self, conn_str: str, table_or_query: str, is_query: bool = False) -> Optional[pd.DataFrame]:
        """Fetch data from SQL using SQLAlchemy connection string.
        If `is_query` is True, `table_or_query` is treated as a full SQL query.
        """
        if create_engine is None:
            st.error("SQL support requires SQLAlchemy. Установите пакет 'sqlalchemy'.")
            return None

        try:
            engine = create_engine(conn_str)
            if is_query:
                df = pd.read_sql_query(table_or_query, engine)
            else:
                # treat as table name
                df = pd.read_sql_table(table_or_query, engine)
            return df
        except Exception as e:
            st.error(f"Ошибка при чтении из базы данных: {e}")
            return None

    def apply_theme(self):
        """Apply selected theme"""
        if self.theme == "Dark":
            bg_color = '#000000'
            text_color = '#FFFFFF'
        else:
            bg_color = '#FFFFFF'
            text_color = '#000000'
        
        font_family = "'Calibri', 'Segoe UI'"
        inject_css(font_family, bg_color, text_color)
        return bg_color, text_color

    def render_main(self):
        st.title("Сибинтек-софт | Дашборд: загрузка и диаграмма")

        tab1, tab2, tab3 = st.tabs(["Диаграмма", "Данные", "Настройки"])

        # ---------- Settings tab ----------
        with tab3:
            st.subheader("⚙️ Настройки")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📁 Загрузка данных")
                uploaded_file = st.file_uploader("Загрузите CSV или Excel", type=['csv', 'xlsx'])
                if self.auto_file and uploaded_file is None and self.data is None:
                    self.data = self.load_data(self.auto_file)
                if uploaded_file is not None:
                    self.data = self.load_data(uploaded_file)

            with col2:
                st.subheader("🎨 Тема")
                theme = st.radio(
                    "Выберите тему:",
                    ["Тёмная (Dark)", "Светлая (Light)"],
                    horizontal=True
                )
                self.theme = "Dark" if "Dark" in theme else "Light"

                st.markdown("---")
                st.subheader("Обновление")
                auto_refresh = st.checkbox("Автообновление", value=False)
                refresh_interval = st.slider("Интервал обновления (сек)", min_value=5, max_value=600, value=10)
                refresh_now = st.button("Обновить сейчас")

                # Autosave settings (stored via widget keys in session_state)
                autosave_enabled = st.checkbox("Автосохранение изменений (CSV)", value=False, key='autosave_checkbox')
                autosave_path_input = st.text_input("Путь автосохранения", value="data/raw/saved_data.csv", key='autosave_path_input')

            st.info("Измените тему и загрузите данные в настройках выше")

        # Apply theme and get colors
        bg_color, text_color = self.apply_theme()

        # ---------- DB fetching and caching (if configured via CLI/integration) ----------
        if self.db_conn and self.db_table:
            last_key = 'db_last_fetch'
            data_key = 'db_cached'
            now = datetime.utcnow()

            need_fetch = False
            if refresh_now:
                need_fetch = True
            if data_key not in st.session_state:
                need_fetch = True
            else:
                last = st.session_state.get(last_key)
                if isinstance(last, float):
                    last_dt = datetime.utcfromtimestamp(last)
                elif isinstance(last, datetime):
                    last_dt = last
                else:
                    last_dt = None
                if last_dt is None:
                    need_fetch = True
                else:
                    if (now - last_dt) > timedelta(seconds=refresh_interval):
                        if auto_refresh:
                            need_fetch = True

            if need_fetch:
                df = self.fetch_data_from_sql(self.db_conn, self.db_table, is_query=self.db_is_query)
                if df is not None:
                    st.session_state[data_key] = df
                    st.session_state[last_key] = datetime.utcnow()

            if auto_refresh:
                if st_autorefresh is not None:
                    st_autorefresh(interval=refresh_interval * 1000, key='autorefresh')
                else:
                    st.markdown(
                        f"<script>setInterval(function(){{window.location.reload();}}, {refresh_interval * 1000});</script>",
                        unsafe_allow_html=True,
                    )
                    st.caption("Автообновление работает через перезагрузку страницы (JS fallback)")

            if data_key in st.session_state:
                self.data = st.session_state[data_key]

        # If no data yet, show a warning and exit
        if self.data is None:
            st.warning("Пожалуйста, загрузите файл или подключитесь к SQL в вкладке 'Настройки'")
            return

        # ---------- Data tab (редактируемая таблица) ----------
        with tab2:
            st.subheader("📋 Исходные данные")

            # Try to use the newer editable data editor if available, fall back to dataframe
            edited = None
            try:
                if hasattr(st, 'data_editor'):
                    edited = st.data_editor(self.data, use_container_width=True)
                else:
                    # experimental API in older Streamlit versions
                    edited = st.experimental_data_editor(self.data, num_rows="dynamic")
            except Exception:
                # If any editor isn't available or fails, show read-only dataframe
                st.dataframe(self.data, use_container_width=True)
                edited = self.data

            # If user edited the table in the UI, update internal state
            if edited is not None:
                try:
                    # some editors return a copy / DataFrame-like object
                    self.data = edited.copy() if hasattr(edited, 'copy') else pd.DataFrame(edited)
                except Exception:
                    # fallback: keep original
                    pass

            # Save / Export controls
            col_save, col_download = st.columns([1, 1])
            with col_save:
                if st.button('Сохранить (CSV)'):
                    save_path = Path('data/raw/saved_data.csv')
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        self.data.to_csv(save_path, index=False)
                        st.success(f'Данные сохранены в {save_path}')
                    except Exception as e:
                        st.error(f'Ошибка сохранения: {e}')

            with col_download:
                try:
                    csv_bytes = self.data.to_csv(index=False).encode('utf-8')
                    st.download_button('Скачать CSV', data=csv_bytes, file_name='data_export.csv', mime='text/csv')
                except Exception:
                    st.write('Нет данных для скачивания')

            # Autosave if enabled in settings (stored in session_state keys)
            try:
                autosave_on = st.session_state.get('autosave_checkbox', False)
                autosave_path = st.session_state.get('autosave_path_input', 'data/raw/saved_data.csv')
            except Exception:
                autosave_on = False
                autosave_path = 'data/raw/saved_data.csv'

            if edited is not None and autosave_on:
                try:
                    save_path = Path(autosave_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    self.data.to_csv(save_path, index=False)
                    st.success(f'Автосохранено: {save_path}')
                except Exception as e:
                    st.error(f'Ошибка автосохранения: {e}')

        # ---------- Chart tab ----------
        with tab1:
            st.subheader("Круговая диаграмма")

            cols = list(self.data.columns)
            col_main, col_agg, col_value = st.columns(3)

            with col_main:
                cat_col = st.selectbox('Категория для диаграммы', cols, index=0)

            with col_agg:
                agg_option = st.selectbox('Агрегация', ['Count', 'Sum', 'Mean'])

            value_col = None
            with col_value:
                if agg_option in ('Sum', 'Mean'):
                    numeric_cols = [c for c in cols if pd.api.types.is_numeric_dtype(self.data[c])]
                    if numeric_cols:
                        value_col = st.selectbox('Столбец значений', numeric_cols)
                    else:
                        st.warning('Нет числовых столбцов')
                        agg_option = 'Count'
                else:
                    st.write(" ")

            if agg_option == 'Count':
                counts = self.data[cat_col].value_counts()
            else:
                if value_col is None:
                    counts = self.data[cat_col].value_counts()
                else:
                    if agg_option == 'Sum':
                        counts = self.data.groupby(cat_col)[value_col].sum().sort_values(ascending=False)
                    else:
                        counts = self.data.groupby(cat_col)[value_col].mean().sort_values(ascending=False)

            fig, ax = plt.subplots(figsize=(8, 6))
            colors = plt.cm.tab20.colors

            # Set chart and axes background to current theme background
            fig.patch.set_facecolor(bg_color)
            ax.set_facecolor(bg_color)

            # Draw pie without labels or numeric annotations (hide data on chart)
            wedges = ax.pie(
                counts.values,
                labels=None,
                startangle=90,
                colors=colors[:len(counts)],
                wedgeprops={"edgecolor": bg_color}
            )

            # Equal aspect for circular pie
            ax.axis('equal')

            # Legend outside the chart with readable text color
            legend = ax.legend(
                counts.index,
                title=cat_col,
                bbox_to_anchor=(1.05, 0.5),
                loc='center left',
                frameon=False
            )
            if legend:
                for txt in legend.get_texts():
                    txt.set_color(text_color)
                if legend.get_title():
                    legend.get_title().set_color(text_color)

            # Remove any labels/text drawn on the wedges
            for txt in ax.texts:
                txt.set_visible(False)

            st.pyplot(fig)

    def run(self):
        self.render_main()


def main_entry_point(file_path: Optional[str] = None):
    app = SimpleDashboard(auto_file=file_path)
    app.run()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Simple Streamlit dashboard runner')
    parser.add_argument('--file', '-f', type=str, help='Path to CSV/XLSX file to auto-load')
    parser.add_argument('--db', type=str, help='SQLAlchemy DB connection string (optional)')
    parser.add_argument('--table', type=str, help='Table name or SQL query to load from DB (optional)')
    parser.add_argument('--query', action='store_true', help='Treat --table as full SQL query when set')
    args = parser.parse_args()

    app = SimpleDashboard(auto_file=args.file, db_conn=args.db, db_table=args.table, db_is_query=args.query)
    app.run()
