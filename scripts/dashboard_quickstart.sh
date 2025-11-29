#!/bin/bash
# Быстрый старт для дашборда

echo "🚀 Примеры использования дашборда"
echo "=================================="
echo ""

echo "1️⃣  Интерактивный режим:"
echo "   streamlit run web/app.py"
echo ""

echo "2️⃣  С автоматической загрузкой файла:"
echo "   streamlit run web/app.py -- --auto-load /path/to/data.csv"
echo ""

echo "3️⃣  Через скрипт runner:"
echo "   python scripts/run_dashboard.py --file /path/to/data.csv"
echo ""

echo "4️⃣  Отслеживание директории:"
echo "   python scripts/run_dashboard.py --watch /path/to/directory"
echo ""

echo "5️⃣  Из Python скрипта:"
echo "   from scripts.dashboard_integration import process_and_display"
echo "   process_and_display('/path/to/data.csv')"
echo ""

echo "📖 Полная документация: DASHBOARD_GUIDE.md"
