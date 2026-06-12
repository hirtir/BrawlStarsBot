# Brawl Stars Auto-Clicker (BlueStacks)

Автоматический цикл игр: start → play → бой → выход → повтор.

## Запуск

```
python brawl_stars_bot.py
```

Переключитесь на BlueStacks в течение 5 секунд.

## Остановка

- **F6** или **Ctrl+C**

## Настройка

1. `config.py` — координаты зон джойстика/атаки, таймауты, шаблоны кнопок
2. `setup_battle_area.py` — настройка зоны джойстика (2 нажатия Пробел)
3. `find_coords.py` — показывает координаты мыши в реальном времени
4. `images/` — скриншоты кнопок интерфейса (start, play, next, ok, exit_menu, ult, giper, again, pobedi)
5. `images/case/` — скриншоты кейсов

## Тесты

```
python test_all_templates.py          # проверка файлов
python test_all_templates.py --screen # проверка на экране
python test_battle.py                 # тест только боя (без выбора бойцов)
```
