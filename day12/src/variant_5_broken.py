"""
Вариант №5 - Исходный код с ошибками
Ошибки: StopIteration, битовый сдвиг, RecursionError, утечка памяти
"""

import tracemalloc

# Глобальный кеш для демонстрации утечки памяти
_global_cache = {}
_cache_size = 0


def generate_data_batch(batch_size, total_batches):
    """
    Генератор с ошибкой StopIteration
    ОШИБКА 1: при вызове next() после исчерпания возникает StopIteration
    """
    for batch_num in range(total_batches):
        data = []
        for i in range(batch_size):
            value = 1 << i
            data.append(value)
        yield data
    # Генератор заканчивается, но нет обработки StopIteration


def process_data_value(value, multiplier=2):
    """
    ОШИБКА 2: неправильный битовый сдвиг
    Должно быть value * multiplier, а используется value >> multiplier
    """
    result = value >> multiplier  # ОШИБКА: должен быть *
    return result


def deep_calc(n, depth=0):
    """
    ОШИБКА 3: бесконечная рекурсия (RecursionError)
    Нет корректного условия выхода, только проверка глубины > 100
    """
    if depth > 100:  # ОШИБКА: условие выхода слишком позднее
        return n

    global _cache_size
    key = f"deep_{n}_{depth}"
    if key not in _global_cache:
        _global_cache[key] = n * depth
        _cache_size += 1

    # ОШИБКА: рекурсивный вызов без ограничения по значению n
    return deep_calc(n + 1, depth + 1)


def create_processor_with_leak():
    """
    ОШИБКА 4: утечка памяти через замыкание
    Список cache растет бесконечно
    """
    cache = []

    def processor(data):
        processed = [x * 2 for x in data]
        cache.append(processed)  # ОШИБКА: бесконечное накопление

        # ОШИБКА: неправильный битовый сдвиг
        if len(data) > 10:
            hash_value = 0
            for x in data:
                hash_value = hash_value << 1 ^ x  # Ошибка в сдвиге
            return hash_value
        return len(data)

    return processor


def process_main(batch_count=5, batch_size=10):
    """Главная функция с вызовом всех проблемных участков"""
    print(f"Начинаем обработку {batch_count} партий по {batch_size} элементов")

    # Запуск отслеживания памяти
    tracemalloc.start()

    results = []

    # 1. Проблемный генератор
    gen = generate_data_batch(batch_size, batch_count)

    # ОШИБКА: +1 вызовет StopIteration на последней итерации
    for batch_num in range(batch_count + 1):
        try:
            batch = next(gen)
            print(f"Партия {batch_num}: получено {len(batch)} элементов")

            # 2. Ошибка с битовым сдвигом
            processed_batch = []
            for val in batch:
                processed = process_data_value(val, 2)
                processed_batch.append(processed)

            # 3. Проблемная рекурсия
            try:
                deep_result = deep_calc(0, 0)
                processed_batch.append(deep_result)
            except RecursionError as e:
                print(f"RecursionError поймана: {e}")

            results.append(processed_batch)

        except StopIteration as e:
            print(f"StopIteration поймана: {e}")
            break

    # 4. Утечка через замыкание
    processor = create_processor_with_leak()
    for i in range(10):
        test_data = list(range(100))
        processor(test_data)

    # Вывод статистики памяти
    snapshot = tracemalloc.take_snapshot()
    print("\n=== ТОП-10 ПОТРЕБЛЕНИЯ ПАМЯТИ ===")
    for stat in snapshot.statistics('lineno')[:10]:
        print(stat)

    return results


if __name__ == "__main__":
    try:
        result = process_main(3, 5)
        print(f"Результат: {len(result)} обработанных партий")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()