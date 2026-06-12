# -*- coding: utf-8 -*-
"""
Переключатель бойцов.
Видит «БОЙЦЫ» → назад → смена бойца → play.
"""

import os
import sys
import time

import cv2  # noqa: F401
import keyboard
import pyautogui

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")
CONFIDENCE = 0.5

SELECT_BUTTON = (280, 500)
GRID_START = (500, 350)
GRID_STEP_X = 440
GRID_STEP_Y = 365
GRID_COLS = 3
GRID_ROWS = 2

SWITCH_DELAY = 0.5

_brawler_index = 0
_stop = False


def _on_stop(*_args):
    global _stop
    _stop = True
    print("\n[!] Стоп.")


def find_on_screen(filename: str, timeout: float = 5.0) -> pyautogui.Box | None:
    path = os.path.join(IMAGES_DIR, filename)
    if not os.path.isfile(path):
        print(f"[ОШИБКА] Нет файла: {path}")
        return None

    deadline = time.time() + timeout
    while time.time() < deadline:
        if _stop:
            return None
        try:
            box = pyautogui.locateOnScreen(path, confidence=CONFIDENCE, grayscale=False)
            if box is not None:
                return box
        except pyautogui.ImageNotFoundException:
            pass
        except ValueError:
            pass
        time.sleep(0.4)
    return None


def click_on(filename: str, timeout: float = 5.0) -> bool:
    box = find_on_screen(filename, timeout)
    if box is None:
        return False
    x, y = pyautogui.center(box)
    pyautogui.click(x, y)
    print(f"[OK] Клик {filename} ({x}, {y})")
    return True


def get_grid_pos(index: int) -> tuple[int, int]:
    col = index % GRID_COLS
    row = index // GRID_COLS
    x = GRID_START[0] + col * GRID_STEP_X
    y = GRID_START[1] + row * GRID_STEP_Y
    return x, y


def main():
    global _brawler_index

    print("=" * 50)
    print("  Переключатель бойцов")
    print("=" * 50)
    print("F6 или Ctrl+C — стоп")
    print("Переключитесь на BlueStacks (главное меню)...")
    print()

    keyboard.add_hotkey("f6", _on_stop)

    total = GRID_COLS * GRID_ROWS

    try:
        while not _stop:
            if not find_on_screen("boytsi.png", timeout=3.0):
                continue

            print(f"\n[...] Найдена «БОЙЦЫ» — цикл смены бойца #{_brawler_index + 1}")

            click_on("boytsi.png", timeout=1.0)
            time.sleep(SWITCH_DELAY)

            print("[...] Назад/Пауза...")
            click_on("nazad.png", timeout=3)
            time.sleep(SWITCH_DELAY)

            print(f"[...] Выбор бойца #{_brawler_index + 1}")
            bx, by = get_grid_pos(_brawler_index)
            pyautogui.click(bx, by)
            time.sleep(SWITCH_DELAY)
            print(f"[OK] Позиция ({bx}, {by})")

            click_on("vybrat.png", timeout=3)
            time.sleep(SWITCH_DELAY)

            print("[...] Play!")
            click_on("play_green.png", timeout=3)
            time.sleep(7.0)

            _brawler_index = (_brawler_index + 1) % total
            print(f"[OK] Готово. Следующий: #{_brawler_index + 1}")

    except KeyboardInterrupt:
        pass
    finally:
        keyboard.unhook_all_hotkeys()
        print("\n[ГОТОВО]")


if __name__ == "__main__":
    main()
