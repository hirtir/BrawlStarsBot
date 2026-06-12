# -*- coding: utf-8 -*-
"""
Brawl Stars Bot — Android APK version.
Uses ADB for screen capture and touch events + OpenCV for template matching.
"""

import os
import sys
import time
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None
    np = None

try:
    from adbutils import adb as adb_client
except ImportError:
    adb_client = None

IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")


def adb_shell(cmd: str) -> str:
    if adb_client is None:
        return ""
    try:
        device = adb_client.device()
        return device.shell(cmd).output.strip()
    except Exception:
        return ""


def adb_tap(x: int, y: int):
    adb_shell(f"input tap {x} {y}")


def adb_screenshot() -> "np.ndarray | None":
    if cv2 is None or adb_client is None:
        return None
    try:
        device = adb_client.device()
        raw = device.shell("screencap -p", timeout=10).output
        img_array = np.frombuffer(raw, dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception:
        return None


def find_template(screenshot: "np.ndarray", template_path: str, confidence: float = 0.5):
    if cv2 is None or not os.path.isfile(template_path):
        return None
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        return None
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= confidence:
        h, w = template.shape[:2]
        cx = max_loc[0] + w // 2
        cy = max_loc[1] + h // 2
        return (cx, cy, max_val)
    return None


class BrawlerSwitcherApp(App):
    status_text = StringProperty("Ожидание...")
    grid_info = StringProperty("3x2")
    log_text = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._running = False
        self._thread = None
        self._brawler_index = 0
        self._log_lines = []

    def build(self):
        self.title = "Brawl Stars Bot"
        from brawlstars import root as kv_root
        return kv_root

    def _log(self, msg: str):
        self._log_lines.append(msg)
        if len(self._log_lines) > 10:
            self._log_lines = self._log_lines[-10:]
        self.log_text = "\n".join(self._log_lines)

    def _get_config(self):
        return {
            "cols": int(self.root.ids.cols_input.text or 3),
            "rows": int(self.root.ids.rows_input.text or 2),
            "delay": float(self.root.ids.delay_input.text or 7),
            "select_x": int(self.root.ids.select_x.text or 280),
            "select_y": int(self.root.ids.select_y.text or 500),
            "grid_x": int(self.root.ids.grid_x.text or 500),
            "grid_y": int(self.root.ids.grid_y.text or 350),
            "step_x": int(self.root.ids.step_x.text or 440),
            "step_y": int(self.root.ids.step_y.text or 365),
        }

    def _grid_pos(self, cfg, index):
        col = index % cfg["cols"]
        row = index // cfg["cols"]
        x = cfg["grid_x"] + col * cfg["step_x"]
        y = cfg["grid_y"] + row * cfg["step_y"]
        return x, y

    def start_bot(self):
        if self._running:
            return
        self._running = True
        self._brawler_index = 0
        self.status_text = "Запуск..."
        self._log("Запуск бота...")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop_bot(self):
        self._running = False
        self.status_text = "Остановлен"
        self._log("Остановка...")

    def _run_loop(self):
        cfg = self._get_config()
        total = cfg["cols"] * cfg["rows"]

        Clock.schedule_once(lambda dt: self._log(f"Сетка {cfg['cols']}x{cfg['rows']}, всего {total} позиций"))

        while self._running:
            screenshot = adb_screenshot()
            if screenshot is None:
                time.sleep(1)
                continue

            boytsi = find_template(screenshot, os.path.join(IMAGES_DIR, "boytsi.png"), 0.5)
            if boytsi is None:
                time.sleep(1)
                continue

            Clock.schedule_once(lambda dt: self._log(f"Найдена «БОЙЦЫ» — боец #{self._brawler_index + 1}"))
            Clock.schedule_once(lambda dt: setattr(self, 'status_text', f'Боец #{self._brawler_index + 1}/{total}'))

            adb_tap(boytsi[0], boytsi[1])
            time.sleep(0.5)

            screenshot = adb_screenshot()
            if screenshot:
                nazad = find_template(screenshot, os.path.join(IMAGES_DIR, "nazad.png"), 0.5)
                if nazad:
                    Clock.schedule_once(lambda dt: self._log("Назад"))
                    adb_tap(nazad[0], nazad[1])
                    time.sleep(0.5)

            bx, by = self._grid_pos(cfg, self._brawler_index)
            Clock.schedule_once(lambda dt: self._log(f"Клик позиция ({bx}, {by})"))
            adb_tap(bx, by)
            time.sleep(0.5)

            screenshot = adb_screenshot()
            if screenshot:
                vybrat = find_template(screenshot, os.path.join(IMAGES_DIR, "vybrat.png"), 0.5)
                if vybrat:
                    Clock.schedule_once(lambda dt: self._log("ВЫБРАТЬ"))
                    adb_tap(vybrat[0], vybrat[1])
                    time.sleep(0.5)

            screenshot = adb_screenshot()
            if screenshot:
                play = find_template(screenshot, os.path.join(IMAGES_DIR, "play_green.png"), 0.5)
                if play:
                    Clock.schedule_once(lambda dt: self._log("Play!"))
                    adb_tap(play[0], play[1])
                    time.sleep(cfg["delay"])

            self._brawler_index = (self._brawler_index + 1) % total
            Clock.schedule_once(lambda dt: self._log(f"Готово. Следующий: #{self._brawler_index + 1}"))

        Clock.schedule_once(lambda dt: setattr(self, 'status_text', "Остановлен"))


if __name__ == "__main__":
    BrawlerSwitcherApp().run()
