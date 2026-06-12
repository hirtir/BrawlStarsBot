# -*- coding: utf-8 -*-
"""
Помощник: настройка BATTLE_AREA за 2 нажатия Пробел.

Запуск: python setup_battle_area.py

Для BlueStacks выделяйте НЕ всю карту, а только зону джойстика
(маленький квадрат/круг слева снизу, куда палец водят для ходьбы).

1. Откройте бой в BlueStacks.
2. Левый верхний угол джойстика → ПРОБЕЛ.
3. Правый нижний угол джойстика → ПРОБЕЛ.
4. Скопируйте блок в config.py → BATTLE_AREA
"""

import keyboard
import pyautogui

points: list[tuple[int, int]] = []


def on_space(_event):
    x, y = pyautogui.position()
    points.append((x, y))
    n = len(points)
    print(f"\nТочка {n}: X={x}, Y={y}")

    if n == 1:
        print("Теперь наведите на ПРАВЫЙ НИЖНИЙ угол джойстика и снова ПРОБЕЛ.")
        return

    x1, y1 = points[0]
    x2, y2 = points[1]
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    print("\n" + "=" * 50)
    print("Вставьте в config.py (BATTLE_AREA — джойстик, ATTACK_AREA — стрельба справа):\n")
    print("BATTLE_AREA = {")
    print(f'    "left": {left},')
    print(f'    "top": {top},')
    print(f'    "width": {width},')
    print(f'    "height": {height},')
    print("}")
    print()
    print("# Для атаки запустите скрипт ещё раз на зоне СПРАВА снизу и вставьте как ATTACK_AREA:")
    print("ATTACK_AREA = {")
    print(f'    "left": {left},')
    print(f'    "top": {top},')
    print(f'    "width": {width},')
    print(f'    "height": {height},')
    print("}")
    print("=" * 50)

    keyboard.unhook_all()
    raise SystemExit(0)


print(__doc__)
print("Сейчас: наведите на ЛЕВЫЙ ВЕРХНИЙ угол зоны джойстика (слева снизу) и нажмите ПРОБЕЛ.")
print("Выход: Esc\n")

keyboard.on_press_key("space", on_space)
keyboard.wait("esc")
