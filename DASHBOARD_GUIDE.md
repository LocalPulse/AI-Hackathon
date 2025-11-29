# 📊 Использование Дашборда - Руководство

## 🎯 Обзор

Обновленное веб-приложение теперь включает:
1. **Шрифт Calibri** для всех текстовых элементов
2. **Улучшенная диаграмма** с точными обозначениями и статистикой
3. **Точка входа программы** для автоматической загрузки файлов из других скриптов

---

## 🚀 Способы Запуска

### 1. Интерактивный режим (ручная загрузка файла)
```bash
streamlit run web/app.py
```

### 2. Автоматическая загрузка конкретного файла
```bash
# Вариант 1: Напрямую через streamlit
streamlit run web/app.py -- --auto-load /path/to/data.csv

# Вариант 2: Через скрипт runner
python scripts/run_dashboard.py --file /path/to/data.csv

# Вариант 3: Для Excel файлов
python scripts/run_dashboard.py --file /path/to/data.xlsx
```

### 3. Отслеживание директории (автоматическая загрузка новых файлов)
```bash
# Ищет все CSV файлы в директории
python scripts/run_dashboard.py --watch /path/to/data/directory

# Поиск с конкретным шаблоном
python scripts/run_dashboard.py --watch /path/to/directory --pattern "*.xlsx"
```

---

## 💻 Использование из других скриптов

### Вариант 1: Простая загрузка файла и запуск дашборда

```python
from scripts.dashboard_integration import process_and_display

# Загружает файл и автоматически запускает дашборд
process_and_display("/path/to/data.csv")
```

### Вариант 2: Обработка данных перед отображением

```python
from scripts.dashboard_integration import DashboardIntegration

integration = DashboardIntegration()

# Обработать файл
data = integration.process_file("/path/to/data.csv")

# Выполнить какие-то преобразования
if data is not None:
    data['new_column'] = data['existing_column'] * 2
    
    # Сохранить обработанные данные
    integration.save_processed_data(data, "processed_data")
    
    # Запустить дашборд с обработанными данными
    integration.launch_dashboard("/data/dashboard_output/processed_data.csv")
```

### Вариант 3: Полный цикл обработки

```python
from scripts.dashboard_integration import DashboardIntegration

integration = DashboardIntegration()

# Все в один вызов
integration.process_and_display(
    input_file="/path/to/raw_data.csv",
    output_name="processed_data"
)
```

### Вариант 4: Пакетная обработка директории

```python
from scripts.dashboard_integration import DashboardIntegration

integration = DashboardIntegration()

# Обработать все CSV файлы в директории
processed = integration.batch_process_directory(
    directory="/data/raw",
    pattern="*.csv"
)

print(f"Обработано {len(processed)} файлов")
```

---

## 📝 Формат данных

Дашборд ожидает данные с минимум следующими колонками:
- **worker_id** или **worker** - ID работника
- **timestamp** - Время действия (автоматически преобразуется в datetime)
- **action_name** - Тип действия (Login, Logout, Task Complete, Error, Break и т.д.)

### Пример CSV файла:
```csv
worker_id,timestamp,action_name
Worker_1,2023-01-01 10:00:00,Login
Worker_2,2023-01-01 10:15:00,Task Complete
Worker_1,2023-01-01 11:30:00,Break
Worker_3,2023-01-01 12:00:00,Logout
```

---

## 🎨 Особенности Улучшенного Дашборда

### Шрифт Calibri
- Применен ко всем текстовым элементам
- Включает заголовки, метрики, таблицы и диаграммы
- Улучшает читаемость и профессиональный вид

### Улучшенная Диаграмма
- 📊 Круговая диаграмма с точными процентами и количеством
- 📈 Дополнительная таблица со статистикой
- 🎨 Оптимизированные цвета для лучшей визуализации
- 📋 Четкие подписи и легенда

### Ключевые Показатели
- Всего Записей
- Количество Работников
- Частое Действие

---

## 🔧 Примеры интеграции с системой

### Пример 1: Интеграция с API
```python
from src.api.main import ProcessRequest
from scripts.dashboard_integration import process_and_display

# После обработки видео в API
def process_video_and_show_dashboard(video_file):
    request = ProcessRequest(source=video_file)
    # ... обработка ...
    
    # Показать результаты в дашборде
    result_csv = "results.csv"  # путь к результатам обработки
    process_and_display(result_csv)
```

### Пример 2: Интеграция с Pipeline
```python
from src.services.pipeline import Pipeline
from scripts.dashboard_integration import DashboardIntegration

integration = DashboardIntegration()

# Запустить pipeline
pipeline = Pipeline(config)
pipeline.run(show=False)

# Загрузить результаты в дашборд
result_file = "pipeline_results.csv"
integration.launch_dashboard(result_file)
```

### Пример 3: Автоматический мониторинг
```python
import time
from pathlib import Path
from scripts.dashboard_integration import DashboardIntegration

integration = DashboardIntegration()

# Отслеживать выходную директорию
while True:
    for csv_file in Path("/output").glob("*.csv"):
        integration.process_and_display(csv_file, output_name=f"monitored_{csv_file.stem}")
    time.sleep(60)
```

---

## ⚙️ Конфигурация

### Встроенные пути:
- 📁 Входные данные: `data/raw/`
- 📁 Выходные данные: `data/dashboard_output/`

### Переменные окружения (опционально):
```bash
export DASHBOARD_INPUT_DIR="/path/to/input"
export DASHBOARD_OUTPUT_DIR="/path/to/output"
```

---

## 🐛 Отладка

### Просмотр логов дашборда:
```bash
streamlit run web/app.py -- --auto-load /path/to/file.csv --logger.level=debug
```

### Проверка доступности файла:
```python
from pathlib import Path
file = Path("/path/to/file.csv")
print(f"Файл существует: {file.exists()}")
print(f"Размер: {file.stat().st_size} байт")
```

---

## 📞 Поддержка

Для вопросов или проблем:
1. Проверьте формат CSV файла
2. Убедитесь, что колонки содержат: `worker_id`, `timestamp`, `action_name`
3. Проверьте права доступа к файлам
4. Просмотрите логи приложения

---

## 🎉 Готово!

Дашборд полностью интегрирован и готов к использованию из любого скрипта в проекте.
