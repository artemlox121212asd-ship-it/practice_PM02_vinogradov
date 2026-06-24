"""
Вариант №5 - Исправленная версия
Все ошибки устранены
"""

import tracemalloc
import logging
from typing import List, Generator

# ============================================
# Настройка логирования
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================
# Константы
# ============================================
_MAX_CACHE_SIZE = 200
_MAX_RECURSION_DEPTH = 50
_MAX_RECURSION_VALUE = 100

# Глобальный кеш с ограничением
_global_cache = {}
_cache_size = 0


# ============================================
# ИСПРАВЛЕНИЕ 1: StopIteration
# ============================================
def generate_data_batch(batch_size: int, total_batches: int) -> Generator:
    """
    Генератор с корректным завершением
    ИСПРАВЛЕНО: правильное количество итераций
    """
    logger.debug(f"Создан генератор: размер={batch_size}, партий={total_batches}")

    for batch_num in range(total_batches):
        data = []
        for i in range(batch_size):
            # Исправлено: правильное вычисление значения
            value = i * 2 + 1
            data.append(value)
        yield data

    logger.debug("Генератор завершен корректно")


# ============================================
# ИСПРАВЛЕНИЕ 2: Битовый сдвиг
# ============================================
def process_data_value(value: int, multiplier: int = 2) -> int:
    """
    ИСПРАВЛЕНО: умножение вместо сдвига
    """
    result = value * multiplier
    logger.debug(f"process_data_value({value}, {multiplier}) = {result}")
    return result


# ============================================
# ИСПРАВЛЕНИЕ 3: RecursionError
# ============================================
def deep_calc(n: int, depth: int = 0,
              max_depth: int = _MAX_RECURSION_DEPTH,
              max_value: int = _MAX_RECURSION_VALUE) -> int:
    """
    ИСПРАВЛЕНО: добавлены корректные условия выхода
    """
    global _cache_size

    # Базовые случаи выхода
    if depth >= max_depth:
        logger.warning(f"Достигнута максимальная глубина рекурсии: {depth}")
        return n

    if n > max_value:
        logger.warning(f"Достигнуто максимальное значение: {n}")
        return n

    # Кеширование с ограничением
    key = f"deep_{n}_{depth}"
    if key not in _global_cache:
        # Ограничение размера кеша
        if _cache_size >= _MAX_CACHE_SIZE:
            logger.debug("Очистка кеша (достигнут лимит)")
            _global_cache.clear()
            _cache_size = 0

        _global_cache[key] = n * depth
        _cache_size += 1

    logger.debug(f"deep_calc: n={n}, depth={depth}, cache_size={_cache_size}")
    return deep_calc(n + 1, depth + 1, max_depth, max_value)


# ============================================
# ИСПРАВЛЕНИЕ 4: Утечка памяти
# ============================================
def create_processor_with_leak(max_size: int = 5):
    """
    ИСПРАВЛЕНО: ограничение размера кеша
    """
    cache = []
    total_processed = 0

    def processor(data: List[int]) -> int:
        nonlocal total_processed

        logger.debug(f"Обработка данных: len={len(data)}")

        # Обработка данных
        processed = [x * 2 for x in data]

        # Ограничение размера кеша (FIFO)
        if len(cache) >= max_size:
            removed = cache.pop(0)
            logger.debug(f"Удален старый элемент из кеша: {len(removed)} элементов")

        cache.append(processed)
        total_processed += len(data)

        logger.debug(f"Размер кеша: {len(cache)}, всего обработано: {total_processed}")

        # ИСПРАВЛЕНО: правильный битовый сдвиг
        if len(data) > 10:
            hash_value = 0
            for x in data:
                hash_value = (hash_value >> 1) ^ x
            return hash_value

        return len(data)

    return processor


# ============================================
# Основная функция
# ============================================
def process_main(batch_count: int = 3, batch_size: int = 5) -> List[List[int]]:
    """Главная функция с исправлениями"""
    logger.info(f"Начинаем обработку {batch_count} партий по {batch_size} элементов")

    # Запуск отслеживания памяти
    tracemalloc.start()
    snapshot_start = tracemalloc.take_snapshot()

    results = []

    # 1. Генератор - ИСПРАВЛЕНО: правильный диапазон
    gen = generate_data_batch(batch_size, batch_count)

    # ИСПРАВЛЕНО: batch_count вместо batch_count + 1
    for batch_num in range(batch_count):
        try:
            batch = next(gen)
            logger.debug(f"Получена партия {batch_num}: {len(batch)} элементов")

            # 2. Обработка данных с правильным умножением
            processed_batch = []
            for val in batch:
                processed = process_data_value(val, 2)
                processed_batch.append(processed)

            # 3. Рекурсия с ограничением
            try:
                deep_result = deep_calc(0, 0)
                processed_batch.append(deep_result)
            except RecursionError as e:
                logger.error(f"RecursionError: {e}")
                processed_batch.append(-1)

            results.append(processed_batch)
            logger.info(f"Партия {batch_num} обработана: {len(processed_batch)} элементов")

        except StopIteration as e:
            logger.error(f"StopIteration: {e}")
            break
        except Exception as e:
            logger.error(f"Неожиданная ошибка в партии {batch_num}: {e}")
            continue

    # 4. Процессор с ограничением кеша
    processor = create_processor_with_leak(max_size=5)
    for i in range(10):
        test_data = list(range(100))
        processor(test_data)
        logger.debug(f"Итерация {i} завершена")

    # Анализ памяти
    snapshot_end = tracemalloc.take_snapshot()

    print("\n=== СТАТИСТИКА ПАМЯТИ ===")
    print("Топ-10 строк по потреблению памяти:")
    for stat in snapshot_end.statistics('lineno')[:10]:
        print(f"  {stat}")

    # Сравнение снимков для выявления утечек
    diff = snapshot_end.compare_to(snapshot_start, 'lineno')
    print("\nТоп-5 изменений (утечек):")
    for stat in diff[:5]:
        print(f"  {stat}")

    logger.info(f"Обработка завершена. Результатов: {len(results)}")
    return results


# ============================================
# Точка входа
# ============================================
if __name__ == "__main__":
    try:
        result = process_main(3, 5)
        print(f"\n✅ Результат: {len(result)} обработанных партий")
        print(f"📊 Размер кеша: {_cache_size}")
        print(f"📊 Содержимое кеша: {len(_global_cache)} записей")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()