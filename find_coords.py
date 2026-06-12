# -*- coding: utf-8 -*-
"""
Вспомогательный скрипт: показывает текущие координаты мыши в реальном времени.
Запуск: python find_coords.py
Наведите курсор на нужную точку и запишите X, Y для config.py
Нажмите Ctrl+C для выхода.
"""

import time

import pyautogui

print("Наведите мышь на нужную точку. Координаты обновляются каждые 0.2 сек.")
print("Ctrl+C — выход.\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"\rX: {x:4d}  Y: {y:4d}", end="", flush=True)
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nГотово.")
