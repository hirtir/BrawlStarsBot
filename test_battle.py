# -*- coding: utf-8 -*-
"""
Тест ТОЛЬКО боя — без выбора персонажей, start, play.

1. python test_battle.py
2. Сами зайдите в бой в BlueStacks
3. Бот двигается и атакует, пока вы не нажмёте F6

Опции:
  python test_battle.py --wait 15
"""

import argparse
import time

import config
from brawl_stars_bot import keyboard, run_battle_loop, setup_hotkeys


def main() -> None:
    parser = argparse.ArgumentParser(description="Тест боя без выбора персонажей")
    parser.add_argument("--wait", type=int, default=10, help="Секунд до старта")
    args = parser.parse_args()

    print("=" * 50)
    print("  ТЕСТ БОЯ (без выбора персонажей)")
    print("=" * 50)
    print()
    print("  1) BlueStacks → сами зайдите в бой")
    print(f"  2) Через {args.wait} сек бот начнёт движение")
    print("  3) Остановка: F6 или Ctrl+C (НЕ ждёт кнопку «Далее»)")
    print()

    for sec in range(args.wait, 0, -1):
        print(f"\rСтарт через {sec:2d} сек... ", end="", flush=True)
        time.sleep(1)
    print("\n")

    setup_hotkeys()
    try:
        run_battle_loop(check_battle_end=False)
    except KeyboardInterrupt:
        print("\n[СТОП] Прервано.")
    finally:
        keyboard.unhook_all_hotkeys()
        print("[ГОТОВО]")


if __name__ == "__main__":
    main()
