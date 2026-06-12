# -*- coding: utf-8 -*-
"""
Настройки автокликера Brawl Stars.
Измените значения под своё разрешение BlueStacks и расположение окна.
"""

import os

# Папка с PNG-шаблонами кнопок (скриншоты интерфейса игры)
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "images")

# Уверенность поиска картинки (0.0–1.0). Требование задания: 0.8
IMAGE_CONFIDENCE = 0.5

# Сколько секунд ждать появления кнопки на экране
BUTTON_SEARCH_TIMEOUT = 60

# Пауза между действиями в бою (секунды) — интервал спама пробелом
BATTLE_CHECK_INTERVAL = 0.25

# Длительность удержания джойстика (зажали и тянем — персонаж идёт)
BATTLE_JOYSTICK_HOLD = 2.5

# Скорость перетаскивания джойстика (секунды)
BATTLE_MOVE_DURATION_MIN = 1.2
BATTLE_MOVE_DURATION_MAX = 1.8

# Удержание кнопки атаки (секунды)
BATTLE_ATTACK_HOLD = 0.35

# Атаковать каждые N циклов (1 = каждый раз, 3 = ходьба×2 + атака×1)
BATTLE_ATTACK_EVERY_N_CYCLES = 1

# Максимальная длительность одного боя (секунды). Защита от зависания.
MAX_BATTLE_DURATION = 400

# Не считать бой оконченным раньше (защита от ложного «Далее» на экране)
MIN_BATTLE_SECONDS = 20

# Сколько раз подряд должна найтись кнопка «Далее», чтобы бой считался кончившимся
POST_BATTLE_CONFIRM_COUNT = 2

# Куда двигать мышь и кликать ВО ВРЕМЯ БОЯ (против AFK-кика).
#
# В BlueStacks движение — это НЕ вся карта, а маленький квадрат слева снизу (виртуальный джойстик).
# Выделите ТОЛЬКО этот квадрат — так и нужно.
#
# Настройка: python setup_battle_area.py
#   1) левый верх угла джойстика → Пробел
#   2) правый низ угла джойстика → Пробел
# Зона движения (джойстик слева снизу)
BATTLE_AREA = {
    "left": 197,
    "top": 706,
    "width": 209,
    "height": 221,
}

# Зона атаки (область прицела/стрельбы справа снизу)
ATTACK_AREA = {
    "left": 1507,
    "top": 627,
    "width": 129,
    "height": 203,
}

# Ульта: видит ult.png → клик в ULT_AREA
ULT_AREA = {
    "left": 1305,
    "top": 697,
    "width": 129,
    "height": 172,
}

# Победа на главном меню → одна катка → поиск кейсов
POBEDI_FILES = ["pobedi.png", "pobedi2.png", "pobedi3.png"]
CASES_DIR = os.path.join(IMAGES_DIR, "case")
CASE_CONFIDENCE = 0.8
CASE_CLICK_COUNT = 15
CASE_CLICK_INTERVAL = 0.5

# Вылет игры: again.png → клик и продолжить с того же места
AGAIN_FILE = "again.png"
AGAIN_CLICK = (692, 608)
AGAIN_CONFIDENCE = 0.8
AGAIN_WAIT_AFTER_CLICK = 3.0

# Сколько ждать главное меню после «Выйти в меню»
MAIN_MENU_WAIT = 2.0

# --- Ротация бойцов (координатная сетка 3x2) ---
BRAWLER_SELECT_BUTTON = (280, 500)

BRAWLER_GRID_START = (500, 350)
BRAWLER_GRID_STEP_X = 440
BRAWLER_GRID_STEP_Y = 365
BRAWLER_GRID_COLS = 3
BRAWLER_GRID_ROWS = 2

BRAWLER_SWITCH_DELAY = 0.5

# Пауза после клика (секунды), чтобы интерфейс успел отреагировать
CLICK_DELAY = 0.8

# Пауза между полными циклами (играми)
LOOP_DELAY = 2.0

# Клавиша аварийной остановки
STOP_HOTKEY = "f6"

# Имена файлов шаблонов в папке images/
# Пауза между кликом start.png и play.png (секунды)
START_TO_PLAY_DELAY = 1.5

# Кнопки в папке images/. Можно список — переберёт все варианты.
# Доп. файлы с суффиксами _2, _3, _alt подхватываются автоматически:
#   start.png + start_2.png + start_3.png
IMAGE_FILES = {
    "igrat": ["igrat.png"],
    "vybrat": ["vybrat.png"],
    "start": ["start.png"],
    "play": ["play.png"],
    "next": ["next.png"],
    "ok": ["ok.png"],
    "continue": ["continue.png"],
    "exit_menu": ["exit_menu.png"],
    "povtorny_vhod": ["povtorny_vhod.png"],
}


