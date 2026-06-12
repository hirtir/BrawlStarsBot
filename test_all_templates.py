# -*- coding: utf-8 -*-
"""
Проверка файлов и (опционально) поиска на экране.

  python test_all_templates.py
  python test_all_templates.py --screen
"""

import os
import sys
import time

import cv2  # noqa: F401

import config
from brawl_stars_bot import (
    _ui_template_paths,
    find_template_on_screen,
)


def _check_files() -> bool:
    print("=" * 60)
    print("ФАЙЛЫ НА ДИСКЕ")
    print("=" * 60)
    ok = True

    print("\nКнопки (images\\):")
    for key in config.IMAGE_FILES:
        paths = _ui_template_paths(key)
        if paths:
            for p in paths:
                print(f"  [OK] {key}: {p}")
        else:
            print(f"  [НЕТ] {key}")
            ok = False

    return ok


def _check_screen() -> None:
    print("\nОткройте главное меню в BlueStacks. Старт через 5 сек...")
    time.sleep(5)
    for key in ("start", "play", "exit_menu"):
        paths = _ui_template_paths(key)
        if not paths:
            continue
        found = find_template_on_screen(paths, 3.0)
        if found:
            print(f"  [ВИДИТ] {key}")
        else:
            print(f"  [НЕ ВИДИТ] {key}")


def main() -> None:
    if not _check_files():
        sys.exit(1)
    if "--screen" in sys.argv:
        _check_screen()
    else:
        print("\nЭкран: python test_all_templates.py --screen")


if __name__ == "__main__":
    main()
