#!/bin/bash
# Быстрый старт для дашборда

echo " Примеры использования дашборда"
echo "=================================="
echo ""

echo " Интерактивный режим:"
echo "   streamlit run web/app.py"
echo ""

echo "С автоматической загрузкой файла:"
echo "   streamlit run web/app.py -- --auto-load /path/to/data.csv"
echo ""

echo "Через скрипт runner:"
echo "   python scripts/run_dashboard.py --file /path/to/data.csv"
echo ""

echo "Отслеживание директории:"
echo "   python scripts/run_dashboard.py --watch /path/to/directory"
echo ""

echo "Из Python скрипта:"
echo "   from scripts.dashboard_integration import process_and_display"
echo "   process_and_display('/path/to/data.csv')"
echo ""

echo "Полная документация: DASHBOARD_GUIDE.md"
