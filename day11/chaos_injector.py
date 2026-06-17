#!/usr/bin/env python3
"""
chaos_injector.py - Скрипт симуляции аварии (Game Day) для Варианта 5.
Удаляет таблицы в тестовом инстансе CockroachDB и симулирует порчу данных в S3.
"""
import os
import sys
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [CHAOS] - %(message)s')
logger = logging.getLogger("ChaosEngine")

def inject_disaster():
    logger.warning("!!! ИНИЦИАЛИЗАЦИЯ СЦЕНАРИЯ КАТАСТРОФЫ: СБОЙ РЕГИОНА AWS !!!")
    
    # 1. Симуляция удаления критических таблиц заказов
    logger.info("Симуляция: DROP TABLE orders CASCADE в тестовой среде...")
    
    # 2. Имитация шифрования / порчи 10% файлов в S3 хранилище каталога товаров
    logger.info("Симуляция: Обнаружено вредоносное шифрование 10% медиа-ассетов (фото товаров)...")
    affected_files = [f"product_image_{random.randint(1000,9999)}.jpg" for _ in range(5)]
    for f in affected_files:
        logger.error(f"Файл зашифрован вымогателем: s3://vsedlyavseh-media/{f}.encrypted")
        
    logger.critical("Авария полностью развернута. Системы переведены в статус DOWN. Начните процедуру восстановления!")

if __name__ == "__main__":
    inject_disaster()