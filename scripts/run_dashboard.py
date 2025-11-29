#!/usr/bin/env python3
"""
Точка входа для запуска дашборда с автоматической загрузкой файлов.

Использование:
    python run_dashboard.py --file /path/to/data.csv
    python run_dashboard.py --watch /path/to/data/directory
    python run_dashboard.py  (интерактивный режим)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class DashboardRunner:
    """Управляет запуском дашборда с различными параметрами"""
    
    def __init__(self, web_app_path=None):
        self.web_app_path = web_app_path or str(Path(__file__).parent.parent / "web" / "app.py")
        
    def run_with_file(self, file_path: str):
        """Запустить дашборд с конкретным файлом"""
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return False
        
        logger.info(f"Запуск дашборда с файлом: {file_path}")
        
        try:
            # Используем streamlit для запуска
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                self.web_app_path,
                "--",
                "--auto-load", file_path
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при запуске дашборда: {e}")
            return False
    
    def run_interactive(self):
        """Запустить дашборд в интерактивном режиме"""
        logger.info("Запуск дашборда в интерактивном режиме")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                self.web_app_path
            ], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Ошибка при запуске дашборда: {e}")
            return False
    
    def watch_directory(self, directory: str, pattern: str = "*.csv"):
        """Отслеживать директорию на новые файлы и автоматически загружать их"""
        watch_path = Path(directory)
        
        if not watch_path.exists():
            logger.error(f"Директория не найдена: {directory}")
            return False
        
        logger.info(f"Отслеживание директории: {directory}")
        logger.info(f"Ищем файлы с шаблоном: {pattern}")
        
        processed_files = set()
        
        while True:
            try:
                # Ищем новые файлы
                for file_path in watch_path.glob(pattern):
                    if file_path.is_file() and str(file_path) not in processed_files:
                        logger.info(f"Найден новый файл: {file_path.name}")
                        processed_files.add(str(file_path))
                        
                        # Запускаем дашборд с новым файлом
                        self.run_with_file(str(file_path))
                
                # Ждем перед следующей проверкой
                time.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Отслеживание завершено пользователем")
                break
            except Exception as e:
                logger.error(f"Ошибка при отслеживании: {e}")
                time.sleep(5)


def main():
    parser = argparse.ArgumentParser(
        description="Запуск аналитического дашборда с автоматической загрузкой файлов"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Путь к CSV или Excel файлу для загрузки"
    )
    parser.add_argument(
        "--watch", "-w",
        type=str,
        help="Директория для отслеживания новых файлов"
    )
    parser.add_argument(
        "--pattern", "-p",
        type=str,
        default="*.csv",
        help="Шаблон поиска файлов (по умолчанию: *.csv)"
    )
    
    args = parser.parse_args()
    runner = DashboardRunner()
    
    if args.file:
        runner.run_with_file(args.file)
    elif args.watch:
        runner.watch_directory(args.watch, args.pattern)
    else:
        runner.run_interactive()


if __name__ == "__main__":
    main()
