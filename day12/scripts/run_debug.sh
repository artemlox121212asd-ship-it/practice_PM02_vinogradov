#!/bin/bash

echo "============================================"
echo "Запуск отладки Варианта №5"
echo "============================================"
echo ""

echo "1. Запуск с pdb и .pdbrc:"
python -m pdb src/variant_5_broken.py

echo ""
echo "2. Запуск с pdb и pdb_commands.txt:"
python -m pdb --command pdb_commands.txt src/variant_5_broken.py

echo ""
echo "3. Запуск с memory_profiler:"
python -m memory_profiler src/variant_5_broken.py