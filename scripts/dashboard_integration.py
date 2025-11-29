"""
Интеграционный модуль для использования дашборда из других скриптов.

Пример использования:
    from scripts.dashboard_integration import DashboardIntegration
    
    integration = DashboardIntegration()
    integration.process_and_display("path/to/data.csv")
"""

import os
import sys
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DashboardIntegration:
    """Интеграция дашборда с другими модулями проекта"""
    
    def __init__(self):
        self.output_dir = PROJECT_ROOT / "data" / "dashboard_output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = PROJECT_ROOT / "data" / "raw"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def process_file(self, input_file: Union[str, Path]) -> Optional[pd.DataFrame]:
        """
        Обработать файл и подготовить данные для дашборда
        
        Args:
            input_file: Путь к CSV или Excel файлу
            
        Returns:
            DataFrame или None в случае ошибки
        """
        try:
            input_file = Path(input_file)
            if not input_file.exists():
                logger.error(f"Файл не найден: {input_file}")
                return None
            
            logger.info(f"Обработка файла: {input_file.name}")
            
            if input_file.suffix.lower() == '.csv':
                data = pd.read_csv(input_file)
            elif input_file.suffix.lower() in ['.xlsx', '.xls']:
                data = pd.read_excel(input_file)
            else:
                logger.error(f"Неподдерживаемый формат файла: {input_file.suffix}")
                return None
            
            logger.info(f"Загружено {len(data)} записей с {len(data.columns)} столбцами")
            return data
            
        except Exception as e:
            logger.error(f"Ошибка при обработке файла: {e}")
            return None
    
    def save_processed_data(self, data: pd.DataFrame, output_name: str) -> Optional[Path]:
        """
        Сохранить обработанные данные в CSV
        
        Args:
            data: DataFrame для сохранения
            output_name: Имя выходного файла
            
        Returns:
            Путь к сохраненному файлу или None в случае ошибки
        """
        try:
            if not output_name.endswith('.csv'):
                output_name += '.csv'
            
            output_path = self.output_dir / output_name
            data.to_csv(output_path, index=False)
            logger.info(f"Данные сохранены в: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных: {e}")
            return None
    
    def launch_dashboard(self, file_path: Union[str, Path]) -> bool:
        """
        Запустить дашборд с конкретным файлом
        
        Args:
            file_path: Путь к файлу для загрузки
            
        Returns:
            True если успешно, False если ошибка
        """
        import subprocess
        
        try:
            dashboard_app = PROJECT_ROOT / "web" / "app.py"
            
            if not dashboard_app.exists():
                logger.error(f"Дашборд не найден: {dashboard_app}")
                return False
            
            logger.info(f"Запуск дашборда с файлом: {file_path}")
            
            subprocess.Popen([
                sys.executable, "-m", "streamlit", "run",
                str(dashboard_app),
                "--",
                "--auto-load", str(file_path)
            ])
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при запуске дашборда: {e}")
            return False
    
    def process_and_display(self, input_file: Union[str, Path], output_name: Optional[str] = None) -> bool:
        """
        Полный цикл: загрузка -> обработка -> сохранение -> запуск дашборда
        
        Args:
            input_file: Путь к исходному файлу
            output_name: Имя для сохранения обработанных данных (опционально)
            
        Returns:
            True если успешно, False если ошибка
        """
        # Загружаем файл
        data = self.process_file(input_file)
        if data is None:
            return False
        
        # Сохраняем обработанные данные если задано имя
        if output_name:
            output_path = self.save_processed_data(data, output_name)
            if output_path is None:
                return False
            display_file = str(output_path)
        else:
            display_file = str(input_file)
        
        # Запускаем дашборд
        return self.launch_dashboard(display_file)
    
    def batch_process_directory(self, directory: Union[str, Path], pattern: str = "*.csv") -> list:
        """
        Обработать все файлы в директории
        
        Args:
            directory: Путь к директории
            pattern: Шаблон поиска файлов
            
        Returns:
            Список обработанных файлов
        """
        directory = Path(directory)
        processed_files = []
        
        if not directory.exists():
            logger.error(f"Директория не найдена: {directory}")
            return processed_files
        
        logger.info(f"Обработка файлов в: {directory}")
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                data = self.process_file(file_path)
                if data is not None:
                    output_name = f"processed_{file_path.stem}"
                    self.save_processed_data(data, output_name)
                    processed_files.append(file_path)
        
        logger.info(f"Обработано {len(processed_files)} файлов")
        return processed_files


# Convenience functions
def process_file(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
    """Быстрая функция для обработки файла"""
    integration = DashboardIntegration()
    return integration.process_file(file_path)


def launch_dashboard(file_path: Union[str, Path]) -> bool:
    """Быстрая функция для запуска дашборда"""
    integration = DashboardIntegration()
    return integration.launch_dashboard(file_path)


def process_and_display(input_file: Union[str, Path], output_name: Optional[str] = None) -> bool:
    """Быстрая функция для полного цикла обработки и отображения"""
    integration = DashboardIntegration()
    return integration.process_and_display(input_file, output_name)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Интеграционный скрипт дашборда")
    parser.add_argument("--file", "-f", type=str, help="Обработать файл")
    parser.add_argument("--launch", "-l", type=str, help="Запустить дашборд с файлом")
    parser.add_argument("--batch", "-b", type=str, help="Обработать все файлы в директории")
    parser.add_argument("--output", "-o", type=str, help="Имя выходного файла")
    
    args = parser.parse_args()
    integration = DashboardIntegration()
    
    if args.file:
        data = integration.process_file(args.file)
        if data is not None and args.output:
            integration.save_processed_data(data, args.output)
    elif args.launch:
        integration.launch_dashboard(args.launch)
    elif args.batch:
        integration.batch_process_directory(args.batch)
