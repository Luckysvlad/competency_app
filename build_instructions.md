# Сборка через PyInstaller

## Подготовка окружения
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Команда сборки (один файл)
**Windows:**
```bash
pyinstaller --noconfirm --clean --name CompetencyApp --windowed --onefile   --add-data "app/data;app/data" --add-data "app/ui;app/ui"   --add-data "app/core;app/core" --add-data "app/reports;app/reports"   --add-data "app/logs;app/logs" app/main.py
```

**macOS/Linux (bash):**
```bash
pyinstaller --noconfirm --clean --name CompetencyApp --windowed --onefile   --add-data "app/data:app/data" --add-data "app/ui:app/ui"   --add-data "app/core:app/core" --add-data "app/reports:app/reports"   --add-data "app/logs:app/logs" app/main.py
```

> Обратите внимание на синтаксис `--add-data` для Windows (`;`) и Unix (`:`).

## Выходные файлы
После сборки бинарник появится в `dist/CompetencyApp(.exe)`. Папка `build/` может быть удалена.

## Советы
- Если шрифты в PDF выглядят неверно, убедитесь, что в системе есть базовые TTF (Arial/DejaVu).
- Для matplotlib никаких специальных бэкендов указывать не требуется — используются Qt‑виджеты.
