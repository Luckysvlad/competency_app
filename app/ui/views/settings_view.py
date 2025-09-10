from __future__ import annotations
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Настройки (упрощённый MVP): пороги уровней редактируются на вкладке 'Левелинг'."))
        info = QTextEdit()
        info.setReadOnly(True)
        info.setPlainText("""- Язык интерфейса: Русский (i18n-словарь можно расширять).
- Цвета уровней L1/L2/L3 определены в БД (таблица levels).
- Логи: logs/app.log; отчёты: app/reports.
- Импорт CSV: раздел 'Сотрудники'.
""")
        lay.addWidget(info)
