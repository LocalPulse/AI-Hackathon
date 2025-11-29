import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import glob
from pathlib import Path
from typing import Optional
import sys
import os

# Add the project root to the python path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_manager import DataManager

class DashboardApp:
    def __init__(self, auto_load_path: Optional[str] = None):
        st.set_page_config(page_title="Аналитический Дашборд", layout="wide")
        self.data_manager = DataManager()
        self.data = None
        self.auto_load_path = auto_load_path
        self._inject_calibri_font()

    def _inject_calibri_font(self):
        """Инъецировать стиль Calibri для всех текстовых элементов"""
        st.markdown(
            """
            <style>
            * {
                font-family: 'Calibri', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            .stApp, .stMetric, .stDataFrame, .stText {
                font-family: 'Calibri', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Calibri', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    def run(self):
        self.render_sidebar()
        self.render_main_content()

    def load_data_from_path(self, file_path: str) -> bool:
        """Загрузить данные из указанного пути"""
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
                return True
            elif file_path.endswith(('.xlsx', '.xls')):
                self.data = pd.read_excel(file_path)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при загрузке файла {file_path}: {e}")
    def load_sample_data(self):
        # Create a sample dataframe for worker actions
        dates = pd.date_range(start="2023-01-01", periods=100, freq='H')
        actions = ["Login", "Logout", "Task Complete", "Error", "Break"]
        workers = [f"Worker_{i}" for i in range(1, 6)]
        
        self.data = pd.DataFrame({
            "worker_id": np.random.choice(workers, size=100),
            "timestamp": dates,
            "action_name": np.random.choice(actions, size=100)
        })
        st.sidebar.success("Пример данных загружен!")

    def render_sidebar(self):
        st.sidebar.header("Загрузка Данных")
        
        # Option to load from shared file
        if st.sidebar.button(" Обновить из Базы Данных"):
            self.data = self.data_manager.get_data()
            st.sidebar.success("Данные обновлены!")

        st.sidebar.markdown("---")
        
        uploaded_file = st.sidebar.file_uploader("Загрузите CSV или Excel файл", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    self.data = pd.read_csv(uploaded_file)
                else:
                    self.data = pd.read_excel(uploaded_file)
                st.sidebar.success("Файл успешно загружен!")
            except Exception as e:
                st.sidebar.error(f"Ошибка при загрузке файла: {e}")
        
        if self.data is None:
             # Try to load default data if nothing else
            self.data = self.data_manager.get_data()
            if self.data.empty:
                 st.sidebar.info("База данных пуста. Загрузите файл или сгенерируйте пример.")
            
            # Optional: Load sample data for demonstration
            if st.sidebar.button("Загрузить пример данных"):
                self.load_sample_data()
        
        st.sidebar.markdown("---")
        with st.sidebar.expander(" Персонализация"):
            bg_color = st.color_picker("Цвет фона", "#000000")
            text_color = st.color_picker("Цвет текста", "#FFFFFF")
            
            # Inject CSS for global customization
            st.markdown(
                f"""
                <style>
                /* Основной фон и текст приложения */
                .stApp {{
                    background-color: {bg_color} !important;
                    color: {text_color} !important;
                }}
                
                /* Все заголовки */
                h1, h2, h3, h4, h5, h6 {{
                    color: {text_color} !important;
                }}
                
                /* Метрики */
                [data-testid="stMetricValue"] {{
                    color: {text_color} !important;
                }}
                [data-testid="stMetricLabel"] {{
                    color: {text_color} !important;
                }}
                
                /* Таблицы данных */
                .stDataFrame {{
                    background-color: {bg_color} !important;
                    color: {text_color} !important;
                }}
                .stDataFrame table {{
                    background-color: {bg_color} !important;
                    color: {text_color} !important;
                }}
                .stDataFrame th {{
                    background-color: {bg_color} !important;
                    color: {text_color} !important;
                }}
                .stDataFrame td {{
                    background-color: {bg_color} !important;
                    color: {text_color} !important;
                }}
                
                /* Вкладки */
                .stTabs [data-baseweb="tab-list"] {{
                    background-color: {bg_color} !important;
                }}
                .stTabs [data-baseweb="tab"] {{
                    color: {text_color} !important;
                }}
                
                
                /* Боковая панель - всегда черная */
                [data-testid="stSidebar"] {{
                    background-color: #000000 !important;
                }}
                
                /* Заголовки и параграфы в боковой панели */
                [data-testid="stSidebar"] h1,
                [data-testid="stSidebar"] h2,
                [data-testid="stSidebar"] h3,
                [data-testid="stSidebar"] p {{
                    color: #FFFFFF !important;
                }}
                
                [data-testid="stSidebar"] .stMarkdown {{
                    color: #FFFFFF !important;
                }}
                
                /* Кнопки в боковой панели */
                [data-testid="stSidebar"] button {{
                    color: #FFFFFF !important;
                    background-color: #1a1a1a !important;
                    border: 1px solid #FFFFFF !important;
                }}
                [data-testid="stSidebar"] button:hover {{
                    background-color: #333333 !important;
                }}
                
                /* Expander в боковой панели */
                [data-testid="stSidebar"] details {{
                    background-color: transparent !important;
                }}
                [data-testid="stSidebar"] summary {{
                    color: #FFFFFF !important;
                    background-color: transparent !important;
                }}
                [data-testid="stSidebar"] summary:hover {{
                    background-color: #1a1a1a !important;
                }}
                
                /* Поля ввода в боковой панели */
                [data-testid="stSidebar"] input {{
                    color: #000000 !important;
                    background-color: #FFFFFF !important;
                }}
                [data-testid="stSidebar"] label {{
                    color: #FFFFFF !important;
                }}
                
                /* Текстовые элементы в основной области */
                .stApp p, .stApp span, .stApp div:not([data-testid="stSidebar"] div), .stApp label {{
                    color: {text_color} !important;
                }}
                
                /* Markdown элементы в основной области */
                .stApp .stMarkdown {{
                    color: {text_color} !important;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )

    def load_sample_data(self):
        # Create a sample dataframe for worker actions
        dates = pd.date_range(start="2023-01-01", periods=100, freq='H')
        actions = ["Login", "Logout", "Task Complete", "Error", "Break"]
        workers = [f"Worker_{i}" for i in range(1, 6)]
        
        self.data = pd.DataFrame({
            "worker_id": np.random.choice(workers, size=100),
            "timestamp": dates,
            "action_name": np.random.choice(actions, size=100)
        })
        st.sidebar.success("Пример данных загружен!")

    def render_main_content(self):
        st.title("Дашборд Активности Работников")

        if self.data is None:
            st.info("Загрузите файл или пример данных, чтобы увидеть дашборд.")
            return

        # Ensure timestamp is datetime
        if 'timestamp' in self.data.columns:
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])

        # Top level metrics
        self.render_metrics()

        # Tabs for different views
        tab1, tab2 = st.tabs(["Логи", "Диаграмма"])

        with tab1:
            self.render_logs()
        
        with tab2:
            self.render_pie_chart()

    def render_metrics(self):
        st.subheader("Ключевые Показатели")
        
        if self.data is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Всего Записей", len(self.data))
            
            with col2:
                unique_workers = self.data['worker_id'].nunique() if 'worker_id' in self.data.columns else 0
                st.metric("Количество Работников", unique_workers)
            
            with col3:
                if 'action_name' in self.data.columns and not self.data['action_name'].empty:
                    mode_series = self.data['action_name'].mode()
                    most_common = mode_series[0] if not mode_series.empty else "-"
                    st.metric("Частое Действие", most_common)
                else:
                    st.metric("Частое Действие", "-")
        
        st.markdown("---")

    def render_logs(self):
        st.subheader("Журнал Логов")
        st.dataframe(self.data, use_container_width=True)

    def render_pie_chart(self):
        st.subheader("Круговая Диаграмма: Распределение Действий Работников")
        
        if 'action_name' in self.data.columns:
            action_counts = self.data['action_name'].value_counts()
            
            # Configure matplotlib with Calibri font
            plt.rcParams['font.family'] = 'Calibri'
            plt.rcParams['font.size'] = 10
            
            fig, ax = plt.subplots(figsize=(10, 7))
            
            # Create pie chart with detailed labels
            colors = plt.cm.Set3(np.linspace(0, 1, len(action_counts)))
            wedges, texts, autotexts = ax.pie(
                action_counts, 
                labels=action_counts.index, 
                autopct='%1.1f%% (%d)',
                startangle=90,
                colors=colors,
                textprops={'fontfamily': 'Calibri', 'fontsize': 10}
            )
            
            # Improve text appearance
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontfamily('Calibri')
            
            for text in texts:
                text.set_fontfamily('Calibri')
                text.set_fontsize(11)
            
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            fig.suptitle('Анализ Действий (Количество и Процент)', fontfamily='Calibri', fontsize=12, fontweight='bold', y=0.98)
            
            plt.tight_layout()
            st.pyplot(fig)
            
            # Additional statistics
            st.markdown("#### Статистика по Действиям:")
            stats_df = pd.DataFrame({
                'Действие': action_counts.index,
                'Количество': action_counts.values,
                'Процент': (action_counts.values / action_counts.sum() * 100).round(2)
            }).reset_index(drop=True)
            st.dataframe(stats_df, use_container_width=True)
        else:
            st.warning("Нет данных 'action_name' для построения диаграммы.")

if __name__ == "__main__":
    import argparse
    
    # Создаем парсер аргументов для автоматической загрузки
    parser = argparse.ArgumentParser(description="Аналитический Дашборд с поддержкой автозагрузки")
    parser.add_argument("--auto-load", "--file", "-f", type=str, help="Путь к файлу для автоматической загрузки (CSV или Excel)")
    parser.add_argument("--watch", "-w", type=str, help="Директория для отслеживания новых файлов")
    
    # Парсим только если есть аргументы командной строки
    if len(sys.argv) > 1:
        args = parser.parse_args()
        auto_load_path = args.auto_load
    else:
        auto_load_path = None
    
    # Запускаем приложение
    app = DashboardApp(auto_load_path=auto_load_path)
    app.run()


def main_entry_point(file_path: Optional[str] = None):
    """
    Точка входа для использования из других скриптов.
    
    Пример использования:
    ├─ from web.app import main_entry_point
    ├─ main_entry_point("/path/to/data.csv")
    """
    app = DashboardApp(auto_load_path=file_path)
    app.run()
