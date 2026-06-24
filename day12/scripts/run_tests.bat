@echo off
echo ============================================
echo Запуск тестов Варианта №5
echo ============================================
echo.

echo Запуск всех тестов:
pytest tests/test_variant_5.py -v

echo.
echo Запуск с покрытием кода:
pytest tests/test_variant_5.py --cov=src --cov-report=html

echo.
echo Отчет о покрытии сохранен в htmlcov/index.html

pause