# -*- coding: utf-8 -*-
"""
Автокликер для Brawl Stars (BlueStacks, Windows).

Цикл работы:
  1. Нажатие «Играть»
  2. Активность в бою (движение мыши + атака)
  3. «Далее» / «ОК» / «Продолжить» → «Выйти в меню»
  4. Следующая игра

Остановка: F6 (настраивается в config.py) или Ctrl+C.
"""

import math
import os
import random
import signal
import sys
import time

import cv2  # noqa: F401 — нужен для confidence в pyautogui
import keyboard
import pyautogui

import config

# Безопасность: движение мыши в угол не должно случайно нажать что-то критичное
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05

# Флаг аварийной остановки (F6 или Ctrl+C)
_stop_requested = False

# Счётчик действий в бою (чередование ходьбы и атаки)
_battle_cycle = 0

# Текущий этап (для восстановления после вылета again.png)
_bot_state = "ожидание"

# Текущий индекс бойца в сетке
_brawler_index = 0


def _request_stop(*_args):
    """Устанавливает флаг остановки."""
    global _stop_requested
    _stop_requested = True
    print("\n[!] Остановка запрошена. Завершение после текущего шага...")


def _check_stop():
    """Прерывает выполнение, если пользователь нажал F6 или Ctrl+C."""
    if _stop_requested:
        raise KeyboardInterrupt("Остановка по горячей клавише")


def _set_state(state: str) -> None:
    global _bot_state
    _bot_state = state


def _template_paths_in_folder(names: list[str], folder: str) -> list[str]:
    return _collect_existing_paths(_expand_template_names(names), [folder])


def _case_template_paths() -> list[str]:
    """Все PNG кейсов в images/case/ (case_01.png, case_02.png, ...)."""
    cases_dir = getattr(config, "CASES_DIR", os.path.join(config.IMAGES_DIR, "case"))
    if not os.path.isdir(cases_dir):
        return []
    paths = []
    for entry in sorted(os.listdir(cases_dir)):
        if entry.lower().endswith(".png"):
            paths.append(os.path.join(cases_dir, entry))
    return paths


def handle_crash_recovery() -> bool:
    """
    Вылет игры: again.png / povtorny_vhod.png → клик → продолжаем с _bot_state.
    """
    crash_files = ["again.png", "povtorny_vhod.png"]
    confidence = getattr(config, "AGAIN_CONFIDENCE", config.IMAGE_CONFIDENCE)

    for filename in crash_files:
        path = os.path.join(config.IMAGES_DIR, filename)
        if not os.path.isfile(path):
            continue

        found = find_template_on_screen([path], timeout=0.4, confidence=confidence)
        if found is None:
            continue

        x, y = getattr(config, "AGAIN_CLICK", (692, 608))
        print(f"[КРАШ] Найден {filename} — клик ({x}, {y}). Продолжаем: {_bot_state}")
        pyautogui.click(x, y)
        time.sleep(getattr(config, "AGAIN_WAIT_AFTER_CLICK", 3.0))
        return True

    return False


def _click_in_area(area: dict, label: str) -> None:
    x, y = _random_point_in_area(area)
    pyautogui.click(x, y)
    time.sleep(config.CLICK_DELAY)
    print(f"[OK] Клик: {label} ({x}, {y})")


def _try_battle_abilities() -> None:
    """Видит ult.png → клик в ULT_AREA."""
    confidence = getattr(config, "ABILITY_CONFIDENCE", config.IMAGE_CONFIDENCE)

    ult_path = os.path.join(config.IMAGES_DIR, "ult.png")
    if os.path.isfile(ult_path):
        if find_template_on_screen([ult_path], timeout=0.3, confidence=confidence):
            _click_in_area(config.ULT_AREA, "Ульта")


def _see_pobedi_on_menu() -> bool:
    """Победа на главном экране (pobedi / pobedi2 / pobedi3)."""
    files = getattr(config, "POBEDI_FILES", ["pobedi.png", "pobedi2.png", "pobedi3.png"])
    paths = _template_paths_in_folder(list(files), config.IMAGES_DIR)
    if not paths:
        return False
    return find_template_on_screen(paths, timeout=1.0) is not None


def _handle_cases_if_visible() -> bool:
    """Нашёл кейс на экране → 15 кликов по центру экрана."""
    paths = _case_template_paths()
    if not paths:
        return False

    confidence = getattr(config, "CASE_CONFIDENCE", config.IMAGE_CONFIDENCE)
    found = find_template_on_screen(paths, timeout=3.0, confidence=confidence)
    if found is None:
        print("[...] Кейс на экране не найден.")
        return False

    _set_state("открытие кейсов")
    box, used = found
    print(f"[OK] Кейс найден: {os.path.basename(used)}")

    sw, sh = pyautogui.size()
    cx, cy = sw // 2, sh // 2
    count = getattr(config, "CASE_CLICK_COUNT", 15)
    interval = getattr(config, "CASE_CLICK_INTERVAL", 0.5)

    print(f"[...] Кликаю центр экрана {count} раз...")
    for i in range(count):
        _check_stop()
        handle_crash_recovery()
        pyautogui.click(cx, cy)
        time.sleep(interval)

    print("[OK] Кейсы обработаны.")
    return True


def _names_from_config_entry(entry: str | list[str]) -> list[str]:
    if isinstance(entry, list):
        return list(entry)
    return [entry]


def _expand_template_names(base_names: list[str]) -> list[str]:
    """Основное имя + варианты _2, _3, _alt."""
    result: list[str] = []
    seen: set[str] = set()
    for name in base_names:
        stem, ext = os.path.splitext(name)
        if not ext:
            ext = ".png"
        variants = [name, f"{stem}_2{ext}", f"{stem}_3{ext}", f"{stem}_alt{ext}"]
        for v in variants:
            if v not in seen:
                seen.add(v)
                result.append(v)
    return result


def _collect_existing_paths(names: list[str], folders: list[str]) -> list[str]:
    paths: list[str] = []
    seen: set[str] = set()
    for folder in folders:
        if not folder:
            continue
        for name in names:
            path = os.path.join(folder, name)
            if os.path.isfile(path) and path not in seen:
                seen.add(path)
                paths.append(path)
    return paths


def _ui_template_paths(image_key: str) -> list[str]:
    """Все PNG для кнопки UI (images/ и варианты _2, _3)."""
    entry = config.IMAGE_FILES[image_key]
    names = _expand_template_names(_names_from_config_entry(entry))
    return _collect_existing_paths(names, [config.IMAGES_DIR])


def _image_path(name: str) -> str:
    """Первый существующий путь к шаблону кнопки (для проверок)."""
    paths = _ui_template_paths(name)
    if paths:
        return paths[0]
    entry = config.IMAGE_FILES[name]
    fn = _names_from_config_entry(entry)[0]
    return os.path.join(config.IMAGES_DIR, fn)



def find_template_on_screen(
    paths: list[str],
    timeout: float,
    *,
    confidence: float | None = None,
    region: tuple[int, int, int, int] | None = None,
) -> tuple[pyautogui.Box, str] | None:
    """Ищет любой из PNG. Возвращает (box, путь_к_файлу) или None."""
    if not paths:
        return None

    conf = confidence if confidence is not None else config.IMAGE_CONFIDENCE
    deadline = time.time() + timeout

    while time.time() < deadline:
        _check_stop()
        for path in paths:
            box = locate_image_file(path, confidence=conf, region=region)
            if box is not None:
                return box, path
        time.sleep(0.4)

    return None


def _needle_size(path: str) -> tuple[int, int]:
    """Размер PNG-шаблона (ширина, высота)."""
    from PIL import Image

    with Image.open(path) as img:
        return img.size


_region_warned: set[str] = set()


def _safe_search_region(
    path: str,
    region: tuple[int, int, int, int] | None,
) -> tuple[int, int, int, int] | None:
    """
    Проверяет, что шаблон влезает в область поиска.
    Если нет — ищем по всему экрану (иначе pyautogui падает с ValueError).
    """
    if region is None:
        return None

    needle_w, needle_h = _needle_size(path)
    _left, _top, reg_w, reg_h = region

    if needle_w <= reg_w and needle_h <= reg_h:
        return region

    if path not in _region_warned:
        _region_warned.add(path)
        name = os.path.basename(path)
        print(
            f"[ПРЕДУПРЕЖДЕНИЕ] {name} ({needle_w}×{needle_h} px) больше области поиска "
            f"({reg_w}×{reg_h} px). Ищем по всему экрану. "
            f"Сожмите PNG до ~60–100 px или увеличьте BRAWLER_SEARCH_REGION."
        )
    return None


def locate_image_file(
    path: str,
    *,
    confidence: float | None = None,
    region: tuple[int, int, int, int] | None = None,
) -> pyautogui.Box | None:
    """Ищет один PNG-файл на экране. Возвращает Box или None."""
    if not os.path.isfile(path):
        return None

    conf = confidence if confidence is not None else config.IMAGE_CONFIDENCE
    region = _safe_search_region(path, region)

    try:
        return pyautogui.locateOnScreen(
            path,
            confidence=conf,
            grayscale=False,
            region=region,
        )
    except pyautogui.ImageNotFoundException:
        return None
    except ValueError as err:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] Ошибка поиска {os.path.basename(path)}: {err}. Повтор без области.")
        try:
            return pyautogui.locateOnScreen(
                path,
                confidence=conf,
                grayscale=False,
            )
        except pyautogui.ImageNotFoundException:
            return None


def find_image_file(
    path: str,
    timeout: float,
    *,
    confidence: float | None = None,
    region: tuple[int, int, int, int] | None = None,
) -> pyautogui.Box | None:
    """Ждёт появления PNG на экране до timeout секунд."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        _check_stop()
        box = locate_image_file(path, confidence=confidence, region=region)
        if box is not None:
            return box
        time.sleep(0.4)
    return None


def click_file(path: str) -> bool:
    """Кликает по центру найденного на экране изображения."""
    box = locate_image_file(path)
    if box is None:
        return False
    x, y = pyautogui.center(box)
    pyautogui.click(x, y)
    time.sleep(config.CLICK_DELAY)
    return True


def find_on_screen(image_key: str, timeout: float | None = None) -> pyautogui.Box | None:
    """Ищет кнопку UI на экране (все варианты PNG)."""
    paths = _ui_template_paths(image_key)
    if not paths:
        print(f"[ОШИБКА] Нет файлов для «{image_key}» в images/")
        print(f"         Ожидается: {config.IMAGE_FILES.get(image_key)} (+ _2, _3)")
        return None

    t = timeout if timeout is not None else config.BUTTON_SEARCH_TIMEOUT
    found = find_template_on_screen(paths, t)
    return found[0] if found else None


def click_image(image_key: str, timeout: float | None = None) -> bool:
    """Находит кнопку UI и кликает (перебирает start.png, start_2.png, ...)."""
    paths = _ui_template_paths(image_key)
    if not paths:
        print(f"[ОШИБКА] Нет PNG для «{image_key}» в папке images/")
        return False

    t = timeout if timeout is not None else config.BUTTON_SEARCH_TIMEOUT
    found = find_template_on_screen(paths, t)
    if found is None:
        print(f"[ПРЕДУПРЕЖДЕНИЕ] «{image_key}» не на экране. Искали:")
        for p in paths:
            print(f"    - {p}")
        return False

    box, used_path = found
    x, y = pyautogui.center(box)
    pyautogui.click(x, y)
    time.sleep(config.CLICK_DELAY)
    print(f"[OK] Клик «{image_key}» ← {os.path.basename(used_path)} ({x}, {y})")
    return True


def click_start_and_play(timeout: float | None = None) -> bool:
    """
    Запуск боя: ищет кнопку «ИГРАТЬ» на экране.
    """
    if not click_image("igrat", timeout=timeout):
        print("[ОШИБКА] Не найдена кнопка «ИГРАТЬ» в images/")
        return False

    return True


def click_any_post_battle_button(timeout: float = 15) -> bool:
    """
    После боя кнопка может называться по-разному.
    Пробуем next → ok → continue по очереди.
    """
    keys = ("next", "ok", "continue")
    deadline = time.time() + timeout

    while time.time() < deadline:
        _check_stop()
        for key in keys:
            paths = _ui_template_paths(key)
            if not paths:
                continue
            found = find_template_on_screen(paths, 1.0)
            if found is not None:
                box, used = found
                x, y = pyautogui.center(box)
                pyautogui.click(x, y)
                time.sleep(config.CLICK_DELAY)
                print(f"[OK] Клик «{key}» ← {os.path.basename(used)} ({x}, {y})")
                return True

        time.sleep(0.5)

    print("[ПРЕДУПРЕЖДЕНИЕ] Кнопка «Далее/ОК/Продолжить» не найдена.")
    return False



def _random_point_in_area(area: dict) -> tuple[int, int]:
    x = random.randint(area["left"], area["left"] + area["width"])
    y = random.randint(area["top"], area["top"] + area["height"])
    return x, y


def _joystick_move() -> None:
    """
    Движение: зажать центр джойстика и потянуть в сторону (как палец на телефоне).
    """
    area = config.BATTLE_AREA
    cx = area["left"] + area["width"] // 2
    cy = area["top"] + area["height"] // 2

    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(0.35, 0.85) * min(area["width"], area["height"]) / 2
    tx = int(cx + radius * math.cos(angle))
    ty = int(cy + radius * math.sin(angle))

    duration = random.uniform(
        config.BATTLE_MOVE_DURATION_MIN,
        config.BATTLE_MOVE_DURATION_MAX,
    )

    pyautogui.moveTo(cx, cy, duration=0.25)
    pyautogui.mouseDown()
    pyautogui.moveTo(tx, ty, duration=duration)
    time.sleep(config.BATTLE_JOYSTICK_HOLD)
    pyautogui.mouseUp()


def _attack() -> None:
    """Атака: зажать в зоне прицела справа."""
    attack_area = getattr(config, "ATTACK_AREA", None)
    if not attack_area:
        return

    x, y = _random_point_in_area(attack_area)
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.mouseDown()
    time.sleep(config.BATTLE_ATTACK_HOLD)
    pyautogui.mouseUp()


def random_battle_action() -> None:
    """Движение + спам пробелом (макрос атаки)."""
    _joystick_move()
    pyautogui.press("space")


def _is_post_battle_screen() -> bool:
    """Есть ли на экране кнопка после боя (next / ok / continue)."""
    for key in ("next", "ok", "continue"):
        paths = _ui_template_paths(key)
        if not paths:
            continue
        found = find_template_on_screen(paths, timeout=0.3)
        if found is not None:
            return True
    return False


def run_battle_loop(*, check_battle_end: bool = True) -> bool:
    """
    Цикл боя: движение и атака.

    check_battle_end=False — только F6/Ctrl+C (для test_battle.py).
    check_battle_end=True  — ещё ждёт кнопку «Далее» после MIN_BATTLE_SECONDS.
    """
    global _battle_cycle
    _battle_cycle = 0
    start = time.time()
    post_battle_hits = 0
    min_seconds = getattr(config, "MIN_BATTLE_SECONDS", 20)
    confirm_need = getattr(config, "POST_BATTLE_CONFIRM_COUNT", 2)

    mode = "до F6" if not check_battle_end else f"до «Далее» (мин. {min_seconds} сек)"
    print(f"[...] Бой идёт ({mode})...")

    while time.time() - start < config.MAX_BATTLE_DURATION:
        _check_stop()
        handle_crash_recovery()

        elapsed = time.time() - start

        _set_state("бой")
        _try_battle_abilities()

        if check_battle_end and elapsed >= min_seconds:
            if _is_post_battle_screen():
                post_battle_hits += 1
                if post_battle_hits >= confirm_need:
                    print(f"[OK] Бой завершён (≈{math.floor(elapsed)} сек).")
                    return True
            else:
                post_battle_hits = 0

        random_battle_action()
        time.sleep(config.BATTLE_CHECK_INTERVAL)

    if check_battle_end:
        print("[ПРЕДУПРЕЖДЕНИЕ] Превышено время боя.")
        return False

    print(f"[OK] Тест боя остановлен (≈{math.floor(time.time() - start)} сек).")
    return True


def wait_for_battle_end() -> bool:
    """Бой до кнопки «Далее» (с защитой от ложного срабатывания)."""
    return run_battle_loop(check_battle_end=True)


def run_one_game(*, open_cases_after: bool = False) -> bool:
    """
    Один полный цикл: смена бойца → start → play → бой → выход в меню.
    open_cases_after=True — после катки искать кейсы (режим pobedi).
    """
    _check_stop()
    handle_crash_recovery()

    _set_state("выбор бойца")
    switch_brawler()

    _set_state("запуск боя")
    if not click_start_and_play():
        return False

    print("[...] Ждём загрузку боя (2.5 сек)...")
    time.sleep(2.5)

    wait_for_battle_end()

    _set_state("после боя")
    handle_crash_recovery()

    for _ in range(5):
        _check_stop()
        handle_crash_recovery()
        if click_any_post_battle_button(timeout=3):
            time.sleep(0.5)

    _set_state("выход в меню")
    if not click_image("exit_menu", timeout=10):
        print("[ПРЕДУПРЕЖДЕНИЕ] «Выйти в меню» не найдена — возможно, уже в меню.")

    menu_wait = getattr(config, "MAIN_MENU_WAIT", 2.0)
    print(f"[...] Ждём загрузку главного меню ({menu_wait} сек)...")
    time.sleep(menu_wait)

    if open_cases_after:
        print("\n=== Режим победы: поиск кейсов ===")
        time.sleep(1.0)
        _handle_cases_if_visible()

    _set_state("главное меню")
    return True


def setup_hotkeys() -> None:
    """Регистрирует F6 для остановки и Ctrl+C через signal."""
    signal.signal(signal.SIGINT, _request_stop)
    keyboard.add_hotkey(config.STOP_HOTKEY, _request_stop)
    print(f"Горячая клавиша остановки: {config.STOP_HOTKEY.upper()} или Ctrl+C")


def _get_brawler_grid_position(index: int) -> tuple[int, int]:
    """Возвращает координаты бойца по индексу в сетке."""
    col = index % config.BRAWLER_GRID_COLS
    row = index // config.BRAWLER_GRID_COLS
    x = config.BRAWLER_GRID_START[0] + col * config.BRAWLER_GRID_STEP_X
    y = config.BRAWLER_GRID_START[1] + row * config.BRAWLER_GRID_STEP_Y
    return x, y


def switch_brawler() -> bool:
    """Переключает бойца на следующего в сетке."""
    global _brawler_index
    total = config.BRAWLER_GRID_COLS * config.BRAWLER_GRID_ROWS

    print(f"[...] Выбор бойца #{_brawler_index + 1} из {total}")

    x, y = config.BRAWLER_SELECT_BUTTON
    pyautogui.click(x, y)
    time.sleep(config.BRAWLER_SWITCH_DELAY)

    bx, by = _get_brawler_grid_position(_brawler_index)
    pyautogui.click(bx, by)
    time.sleep(config.BRAWLER_SWITCH_DELAY)
    print(f"[OK] Боец выбран: позиция ({bx}, {by})")

    if not click_image("vybrat", timeout=5):
        print("[ПРЕДУПРЕЖДЕНИЕ] Кнопка «ВЫБРАТЬ» не найдена")

    _brawler_index = (_brawler_index + 1) % total
    return True


def validate_setup() -> bool:
    """Проверяет наличие обязательных шаблонов перед стартом."""
    missing = []
    for key in ("igrat", "exit_menu"):
        path = _image_path(key)
        if not os.path.isfile(path):
            missing.append(path)

    post_battle = ("next", "ok", "continue")
    has_post = any(os.path.isfile(_image_path(k)) for k in post_battle)
    if not has_post:
        missing.append("images/next.png (или ok.png / continue.png)")

    if missing:
        print("[ОШИБКА] Не хватает файлов:")
        for path in missing:
            print(f"  - {path}")
        return False

    return True


def main() -> None:
    print("=" * 50)
    print("  Brawl Stars Auto-Clicker (BlueStacks)")
    print("=" * 50)
    print("Переключитесь на окно BlueStacks в течение 5 секунд...")
    time.sleep(5)

    if not validate_setup():
        sys.exit(1)

    setup_hotkeys()

    print(f"Режим: автоматический цикл игр")

    try:
        game_count = 0

        while not _stop_requested:
            handle_crash_recovery()
            _set_state("главное меню")

            victory_mode = _see_pobedi_on_menu()
            if victory_mode:
                print("\n[ПОБЕДА] pobedi на главном меню — катка + кейсы")

            game_count += 1
            print(f"\n>>> Игра #{game_count}")
            try:
                run_one_game(open_cases_after=victory_mode)
            except KeyboardInterrupt:
                break

    except KeyboardInterrupt:
        pass
    finally:
        keyboard.unhook_all_hotkeys()
        print("\n[ГОТОВО] Скрипт остановлен.")


if __name__ == "__main__":
    main()
