#!/usr/bin/env bash
# 📚 Справочник команд дашборда

# ============================================
# БЫСТРЫЕ КОМАНДЫ
# ============================================

# 1️⃣  Интерактивный режим (ручная загрузка)
# streamlit run web/app.py

# 2️⃣  Автоматическая загрузка CSV файла
# streamlit run web/app.py -- --auto-load data/raw/sample.csv

# 3️⃣  Через скрипт runner
# python scripts/run_dashboard.py --file /path/to/data.csv

# 4️⃣  Отслеживание директории (автозагрузка новых файлов)
# python scripts/run_dashboard.py --watch data/raw --pattern "*.csv"

# 5️⃣  Пакетная обработка директории
# python scripts/run_dashboard.py --batch data/raw

# 6️⃣  Примеры использования (интерактивное меню)
# python scripts/dashboard_examples.py

# ============================================
# PYTHON API
# ============================================

# Вариант 1: Простой запуск
# python -c "
# from scripts.dashboard_integration import process_and_display
# process_and_display('/path/to/data.csv')
# "

# Вариант 2: С обработкой данных
# python -c "
# from scripts.dashboard_integration import DashboardIntegration
# integration = DashboardIntegration()
# data = integration.process_file('data.csv')
# integration.save_processed_data(data, 'processed')
# integration.launch_dashboard('data/dashboard_output/processed.csv')
# "

# Вариант 3: Пакетная обработка
# python -c "
# from scripts.dashboard_integration import DashboardIntegration
# integration = DashboardIntegration()
# integration.batch_process_directory('data/raw')
# "

# ============================================
# ДЛЯ ДРУГИХ СКРИПТОВ ПРОЕКТА
# ============================================

# Добавить в конец скрипта:
# ```python
# from scripts.dashboard_integration import process_and_display
# 
# # После обработки данных
# process_and_display(output_file)
# ```

# ============================================
# СОЗДАНИЕ ПРИМЕРА ДАННЫХ
# ============================================

# python scripts/dashboard_examples.py
# Выберите опцию 1 для создания примера

# ============================================
# ОТЛАДКА
# ============================================

# Просмотр логов
# streamlit run web/app.py -- --auto-load file.csv --logger.level=debug

# Проверка установки зависимостей
# python -m pip list | grep -E "streamlit|pandas|matplotlib"

# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# Входная директория: data/raw/
# Выходная директория: data/dashboard_output/
# Поддерживаемые форматы: CSV, XLSX, XLS

# ============================================
# ДОКУМЕНТАЦИЯ
# ============================================

# Полное руководство: cat DASHBOARD_GUIDE.md
# История изменений: cat DASHBOARD_CHANGELOG.md
# Примеры: python scripts/dashboard_examples.py

echo "📚 Справочник команд дашборда"
echo "=============================="
echo ""
echo "1. Интерактивный режим:"
echo "   streamlit run web/app.py"
echo ""
echo "2. С автоматической загрузкой:"
echo "   streamlit run web/app.py -- --auto-load /path/to/file.csv"
echo ""
echo "3. Через runner скрипт:"
echo "   python scripts/run_dashboard.py --file /path/to/file.csv"
echo ""
echo "4. Отслеживание директории:"
echo "   python scripts/run_dashboard.py --watch /path/to/directory"
echo ""
echo "5. Примеры использования:"
echo "   python scripts/dashboard_examples.py"
echo ""
echo "📖 Документация: DASHBOARD_GUIDE.md"
echo "📝 История: DASHBOARD_CHANGELOG.md"
