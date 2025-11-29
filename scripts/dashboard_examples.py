"""
Пример использования дашборда из других скриптов.
Этот файл показывает различные способы интеграции дашборда.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def example_1_simple_launch():
    """Пример 1: Простой запуск с файлом"""
    print("=" * 50)
    print("Пример 1: Простой запуск дашборда")
    print("=" * 50)
    
    from scripts.dashboard_integration import launch_dashboard
    
    # Предположим, что файл существует
    file_path = "data/raw/sample_data.csv"
    
    print(f"Запуск дашборда с файлом: {file_path}")
    # launch_dashboard(file_path)


def example_2_process_and_display():
    """Пример 2: Обработка и отображение данных"""
    print("\n" + "=" * 50)
    print("Пример 2: Обработка и отображение данных")
    print("=" * 50)
    
    from scripts.dashboard_integration import DashboardIntegration
    
    integration = DashboardIntegration()
    
    # Путь к исходному файлу
    input_file = "data/raw/sample_data.csv"
    
    print(f"Загрузка файла: {input_file}")
    data = integration.process_file(input_file)
    
    if data is not None:
        print(f"Загружено {len(data)} записей")
        print(f"Столбцы: {list(data.columns)}")
        
        # Сохраняем обработанные данные
        output_path = integration.save_processed_data(data, "example_processed")
        print(f"Сохранено в: {output_path}")
        
        # Запускаем дашборд
        # integration.launch_dashboard(str(output_path))
    else:
        print("Не удалось загрузить файл")


def example_3_batch_processing():
    """Пример 3: Пакетная обработка нескольких файлов"""
    print("\n" + "=" * 50)
    print("Пример 3: Пакетная обработка")
    print("=" * 50)
    
    from scripts.dashboard_integration import DashboardIntegration
    
    integration = DashboardIntegration()
    directory = "data/raw"
    
    print(f"Обработка файлов в директории: {directory}")
    processed_files = integration.batch_process_directory(directory, pattern="*.csv")
    
    print(f"Обработано {len(processed_files)} файлов")
    for file in processed_files:
        print(f"   - {file.name}")


def example_4_custom_processing():
    """Пример 4: Кастомная обработка перед отображением"""
    print("\n" + "=" * 50)
    print("Пример 4: Кастомная обработка")
    print("=" * 50)
    
    from scripts.dashboard_integration import DashboardIntegration
    import pandas as pd
    
    integration = DashboardIntegration()
    
    # Загружаем данные
    data = integration.process_file("data/raw/sample_data.csv")
    
    if data is not None:
        print(f"Исходные данные: {len(data)} записей")
        
        # Выполняем кастомные преобразования
        # Например, фильтруем только успешные действия
        if 'action_name' in data.columns:
            data = data[data['action_name'] != 'Error']
            print(f"После фильтрации: {len(data)} записей (ошибки удалены)")
        
        # Сохраняем результаты
        output_path = integration.save_processed_data(data, "custom_processed")
        print(f"Сохранено в: {output_path}")


def example_5_integration_with_pipeline():
    """Пример 5: Интеграция с pipeline"""
    print("\n" + "=" * 50)
    print("Пример 5: Интеграция с Pipeline")
    print("=" * 50)
    
    print("""
    Пример кода для интеграции с Pipeline:
    
    from src.services.pipeline import Pipeline
    from scripts.dashboard_integration import DashboardIntegration
    
    # Запускаем pipeline
    config = PipelineConfig(source="video.mp4")
    pipeline = Pipeline(config)
    pipeline.run(show=False)
    
    # Показываем результаты в дашборде
    integration = DashboardIntegration()
    integration.launch_dashboard("pipeline_results.csv")
    """)


def create_sample_data():
    """Создать пример данных для тестирования"""
    print("\n" + "=" * 50)
    print("Создание примера данных")
    print("=" * 50)
    
    try:
        import pandas as pd
        import numpy as np
        from datetime import datetime, timedelta
        
        # Создаем примеры данных
        dates = pd.date_range(start="2023-01-01", periods=50, freq='H')
        actions = ["Login", "Logout", "Task Complete", "Error", "Break"]
        workers = [f"Worker_{i}" for i in range(1, 6)]
        
        data = pd.DataFrame({
            "worker_id": np.random.choice(workers, size=50),
            "timestamp": dates,
            "action_name": np.random.choice(actions, size=50)
        })
        
        # Сохраняем в файл
        output_path = PROJECT_ROOT / "data" / "raw" / "sample_data.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output_path, index=False)
        
        print(f"Пример данных создан: {output_path}")
        print(f"   Размер: {len(data)} записей")
        print(f"   Колонки: {list(data.columns)}")
        
    except ImportError:
        print("Требуется установить pandas и numpy")


def main():
    """Главная функция с меню примеров"""
    print("\n" + "🎓 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ДАШБОРДА" + "\n")
    print("1. Создать пример данных")
    print("2. Простой запуск дашборда")
    print("3. Обработка и отображение")
    print("4. Пакетная обработка")
    print("5. Кастомная обработка")
    print("6. Интеграция с Pipeline")
    print("7. Показать все примеры")
    print("0. Выход\n")
    
    choice = input("Выберите пример (0-7): ").strip()
    
    if choice == "1":
        create_sample_data()
    elif choice == "2":
        example_1_simple_launch()
    elif choice == "3":
        example_2_process_and_display()
    elif choice == "4":
        example_3_batch_processing()
    elif choice == "5":
        example_4_custom_processing()
    elif choice == "6":
        example_5_integration_with_pipeline()
    elif choice == "7":
        create_sample_data()
        example_1_simple_launch()
        example_2_process_and_display()
        example_3_batch_processing()
        example_4_custom_processing()
        example_5_integration_with_pipeline()
    elif choice == "0":
        print("До свидания!")
    else:
        print("Неверный выбор")


if __name__ == "__main__":
    main()
