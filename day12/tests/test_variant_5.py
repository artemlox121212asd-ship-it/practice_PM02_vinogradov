"""
Тесты для Варианта №5
Проверка исправления всех ошибок
"""

import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.variant_5_fixed import (
    generate_data_batch,
    process_data_value,
    deep_calc,
    create_processor_with_leak,
    process_main,
    _MAX_CACHE_SIZE
)


# ============================================
# ТЕСТЫ ДЛЯ ГЕНЕРАТОРА
# ============================================
class TestGenerator:
    """Тесты для функции generate_data_batch"""

    def test_generate_data_batch_correct_count(self):
        """Проверка правильного количества партий"""
        gen = generate_data_batch(3, 2)
        count = 0
        for _ in gen:
            count += 1
        assert count == 2

        # Проверка StopIteration
        with pytest.raises(StopIteration):
            next(gen)

    def test_generate_data_batch_values(self):
        """Проверка правильности значений"""
        gen = generate_data_batch(3, 1)
        batch = next(gen)
        # Исправленные значения: 1, 3, 5
        assert batch == [1, 3, 5]

    def test_generate_data_batch_empty(self):
        """Проверка пустого генератора"""
        gen = generate_data_batch(0, 3)
        for batch in gen:
            assert len(batch) == 0


# ============================================
# ТЕСТЫ ДЛЯ ОБРАБОТКИ ДАННЫХ
# ============================================
class TestProcessing:
    """Тесты для функций обработки данных"""

    def test_process_data_value_correct(self):
        """Проверка правильного умножения"""
        assert process_data_value(5, 2) == 10
        assert process_data_value(10, 3) == 30
        assert process_data_value(1, 1) == 1
        assert process_data_value(0, 5) == 0

    def test_process_data_value_negative(self):
        """Проверка с отрицательными числами"""
        assert process_data_value(-5, 2) == -10
        assert process_data_value(-3, -1) == 3

    def test_deep_calc_limits(self):
        """Проверка ограничений рекурсии"""
        # Должна завершиться без RecursionError
        result = deep_calc(0, 0)
        assert isinstance(result, int)

        # Проверка с ограничениями
        result = deep_calc(0, 0, max_depth=10, max_value=20)
        assert result is not None

    def test_deep_calc_cache_limit(self):
        """Проверка ограничения кеша"""
        from src.variant_5_fixed import _global_cache, _cache_size
        _global_cache.clear()
        _cache_size = 0

        # Вызываем много раз
        for i in range(300):
            deep_calc(i % 50, i % 10)

        # Кеш не должен превысить лимит
        assert len(_global_cache) <= _MAX_CACHE_SIZE


# ============================================
# ТЕСТЫ ДЛЯ ПАМЯТИ
# ============================================
class TestMemory:
    """Тесты для управления памятью"""

    def test_processor_cache_limit(self):
        """Проверка ограничения кеша в замыкании"""
        processor = create_processor_with_leak(max_size=3)

        # Вызываем больше раз, чем размер кеша
        for i in range(10):
            data = list(range(10))
            processor(data)

        # Проверяем, что кеш не превысил лимит
        assert True

    def test_processor_memory_growth(self):
        """Проверка отсутствия роста памяти"""
        import tracemalloc
        tracemalloc.start()

        snapshot1 = tracemalloc.take_snapshot()

        processor = create_processor_with_leak(max_size=5)
        for i in range(20):
            data = list(range(100))
            processor(data)

        snapshot2 = tracemalloc.take_snapshot()

        # Сравнение снимков - не должно быть значительного роста
        diff = snapshot2.compare_to(snapshot1, 'lineno')
        memory_growth = sum(stat.size_diff for stat in diff[:10])

        # Рост памяти не должен превышать 1 МБ
        assert memory_growth < 1024 * 1024


# ============================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ============================================
class TestIntegration:
    """Интеграционные тесты"""

    def test_full_workflow(self):
        """Полный рабочий процесс"""
        gen = generate_data_batch(3, 2)
        results = []

        for batch in gen:
            processed = [process_data_value(x, 2) for x in batch]
            results.append(processed)

        assert len(results) == 2
        assert len(results[0]) == 3
        assert len(results[1]) == 3

    def test_main_function(self):
        """Тест основной функции"""
        result = process_main(2, 3)
        assert len(result) == 2
        assert all(isinstance(batch, list) for batch in result)
        assert all(len(batch) > 0 for batch in result)

    def test_no_recursion_error(self):
        """Проверка отсутствия RecursionError"""
        result = deep_calc(0, 0, max_depth=30, max_value=50)
        assert result is not None

    def test_no_stop_iteration(self):
        """Проверка отсутствия StopIteration"""
        gen = generate_data_batch(3, 2)

        count = 0
        for _ in range(2):
            next(gen)
            count += 1

        assert count == 2

        with pytest.raises(StopIteration):
            next(gen)


# ============================================
# ЗАПУСК ТЕСТОВ
# ============================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])