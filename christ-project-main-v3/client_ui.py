import sys
import markdown

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QComboBox, QLabel, QMessageBox,
    QLineEdit, QStackedWidget, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from client import ApiClient


class RequestWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MobileCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class NavButton(QPushButton):
    def __init__(self, text, index, callback):
        super().__init__(text)
        self.index = index
        self.setCheckable(True)
        self.clicked.connect(lambda: callback(index))
        self.setObjectName("navButton")


class ChristianReferenceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.api = ApiClient()
        self.worker = None
        self.nav_buttons = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Справочник священника")
        self.setMinimumSize(390, 780)
        self.resize(430, 820)

        root = QWidget()
        self.setCentralWidget(root)

        self.main_layout = QVBoxLayout(root)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        self.build_header()
        self.build_pages()
        self.build_bottom_nav()
        self.apply_styles()

        self.switch_page(0)

    def build_header(self):
        header = QFrame()
        header.setObjectName("header")

        layout = QVBoxLayout(header)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(4)

        title = QLabel("Справочник священника")
        title.setObjectName("appTitle")

        subtitle = QLabel("Карманный духовный помощник")
        subtitle.setObjectName("appSubtitle")

        self.status_label = QLabel("Готово к работе")
        self.status_label.setObjectName("statusLabel")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.status_label)

        self.main_layout.addWidget(header)

    def build_pages(self):
        self.pages = QStackedWidget()
        self.pages.setObjectName("pages")

        self.random_page = self.create_random_page()
        self.commandments_page = self.create_commandments_page()
        self.search_page = self.create_search_page()
        self.ai_page = self.create_ai_page()

        self.pages.addWidget(self.random_page)
        self.pages.addWidget(self.commandments_page)
        self.pages.addWidget(self.search_page)
        self.pages.addWidget(self.ai_page)

        self.main_layout.addWidget(self.pages, 1)

    def build_bottom_nav(self):
        nav = QFrame()
        nav.setObjectName("bottomNav")

        layout = QHBoxLayout(nav)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        items = [
            ("📖 Писание", 0),
            ("⚖️ Заповеди", 1),
            ("🔎 Поиск", 2),
            ("🤖 AI", 3),
        ]

        for text, index in items:
            btn = NavButton(text, index, self.switch_page)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        self.main_layout.addWidget(nav)

    def create_page_container(self, title_text, subtitle_text=None):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        card = MobileCard()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)

        title = QLabel(title_text)
        title.setObjectName("pageTitle")
        card_layout.addWidget(title)

        if subtitle_text:
            subtitle = QLabel(subtitle_text)
            subtitle.setObjectName("pageSubtitle")
            subtitle.setWordWrap(True)
            card_layout.addWidget(subtitle)

        layout.addWidget(card)
        return page, card, card_layout

    def create_random_page(self):
        page, card, layout = self.create_page_container(
            "Случайное писание дня",
            "Откройте вдохновляющий отрывок из Писания."
        )

        self.scripture_display = QTextEdit()
        self.scripture_display.setReadOnly(True)
        self.scripture_display.setObjectName("contentBox")
        self.scripture_display.setPlaceholderText("Здесь появится случайное писание...")
        layout.addWidget(self.scripture_display, 1)

        self.random_btn = QPushButton("Получить писание")
        self.random_btn.clicked.connect(self.generate_random_scripture)
        layout.addWidget(self.random_btn)

        return page

    def create_commandments_page(self):
        page, card, layout = self.create_page_container(
            "Заповеди",
            "Выберите категорию и получите наставление."
        )

        label = QLabel("Категория")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        self.cmd_category = QComboBox()
        self.cmd_category.addItems(["Все", "Десять заповедей", "Заповеди Иисуса"])
        layout.addWidget(self.cmd_category)

        self.commandments_display = QTextEdit()
        self.commandments_display.setReadOnly(True)
        self.commandments_display.setObjectName("contentBox")
        self.commandments_display.setPlaceholderText("Здесь появится текст заповеди...")
        layout.addWidget(self.commandments_display, 1)

        self.commandment_btn = QPushButton("Получить заповедь")
        self.commandment_btn.clicked.connect(self.get_commandment)
        layout.addWidget(self.commandment_btn)

        return page

    def create_search_page(self):
        page, card, layout = self.create_page_container(
            "Поиск по текстам",
            "Найдите места Писания по слову или теме."
        )

        label = QLabel("Ключевое слово")
        label.setObjectName("fieldLabel")
        layout.addWidget(label)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Например: любовь, вера, милость...")
        search_row.addWidget(self.search_input, 1)

        self.search_btn = QPushButton("Найти")
        self.search_btn.clicked.connect(self.perform_search)
        search_row.addWidget(self.search_btn)

        layout.addLayout(search_row)

        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        self.search_results.setObjectName("contentBox")
        self.search_results.setPlaceholderText("Результаты поиска появятся здесь...")
        layout.addWidget(self.search_results, 1)

        return page

    def create_ai_page(self):
        page, card, layout = self.create_page_container(
            "AI помощник",
            "Задайте вопрос и получите развернутый ответ."
        )

        input_label = QLabel("Ваш вопрос")
        input_label.setObjectName("fieldLabel")
        layout.addWidget(input_label)

        self.ai_input = QTextEdit()
        self.ai_input.setObjectName("inputBox")
        self.ai_input.setMaximumHeight(120)
        self.ai_input.setPlaceholderText("Например: Расскажи о любви в христианстве...")
        layout.addWidget(self.ai_input)

        self.ask_btn = QPushButton("Спросить AI")
        self.ask_btn.clicked.connect(self.ask_ai)
        layout.addWidget(self.ask_btn)

        response_label = QLabel("Ответ")
        response_label.setObjectName("fieldLabel")
        layout.addWidget(response_label)

        self.ai_response = QTextEdit()
        self.ai_response.setReadOnly(True)
        self.ai_response.setObjectName("contentBox")
        self.ai_response.setPlaceholderText("Ответ AI появится здесь...")
        layout.addWidget(self.ai_response, 1)

        return page

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def set_loading_state(self, is_loading, button=None, text="Загрузка..."):
        buttons = [
            self.random_btn,
            self.commandment_btn,
            self.search_btn,
            self.ask_btn
        ]

        for btn in buttons:
            btn.setEnabled(not is_loading)

        if is_loading:
            self.status_label.setText("Выполняется запрос...")
            if button:
                button.setText(text)
        else:
            self.status_label.setText("Готово к работе")
            self.random_btn.setText("Получить писание")
            self.commandment_btn.setText("Получить заповедь")
            self.search_btn.setText("Найти")
            self.ask_btn.setText("Спросить AI")

    def generate_random_scripture(self):
        self.set_loading_state(True, self.random_btn, "Загрузка...")
        self.worker = RequestWorker(self.api.get_random_scripture)
        self.worker.finished.connect(self.on_scripture_loaded)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(lambda _: self.set_loading_state(False))
        self.worker.error.connect(lambda _: self.set_loading_state(False))
        self.worker.start()

    def on_scripture_loaded(self, data):
        if data.get("error"):
            self.scripture_display.setText(data["error"])
            return

        text = (
            f"📖 {data['book']} {data['chapter']}:{data['verse']}\n\n"
            f"“{data['text']}”\n\n"
            f"📝 Категория: {data['category']}"
        )
        self.scripture_display.setText(text)

    def get_commandment(self):
        category = self.cmd_category.currentText()
        self.set_loading_state(True, self.commandment_btn, "Загрузка...")
        self.worker = RequestWorker(self.api.get_random_commandment, category)
        self.worker.finished.connect(self.on_commandment_loaded)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(lambda _: self.set_loading_state(False))
        self.worker.error.connect(lambda _: self.set_loading_state(False))
        self.worker.start()

    def on_commandment_loaded(self, data):
        if data.get("error"):
            self.commandments_display.setText(data["error"])
            return

        text = (
            f"⚖️ Заповедь:\n\n"
            f"“{data['text']}”\n\n"
            f"📚 Источник: {data['reference']}\n"
            f"📌 Категория: {data['category']}"
        )
        self.commandments_display.setText(text)

    def perform_search(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "Предупреждение", "Введите ключевое слово для поиска")
            return

        self.set_loading_state(True, self.search_btn, "Поиск...")
        self.worker = RequestWorker(self.api.search_texts, keyword)
        self.worker.finished.connect(self.on_search_loaded)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(lambda _: self.set_loading_state(False))
        self.worker.error.connect(lambda _: self.set_loading_state(False))
        self.worker.start()

    def on_search_loaded(self, results):
        if isinstance(results, dict) and results.get("error"):
            self.search_results.setText(results["error"])
            return

        if not results:
            self.search_results.setText("Ничего не найдено.")
            return

        text = f"Найдено {len(results)} результатов:\n\n"
        for i, item in enumerate(results, 1):
            preview = item["text"][:120].strip()
            if len(item["text"]) > 120:
                preview += "..."
            text += f"{i}. {item['book']} {item['chapter']}:{item['verse']}\n"
            text += f"   “{preview}”\n\n"

        self.search_results.setText(text)

    def ask_ai(self):
        question = self.ai_input.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Предупреждение", "Введите вопрос")
            return

        self.ai_response.setText("⏳ Подготавливается ответ...")
        self.set_loading_state(True, self.ask_btn, "Отправка...")

        self.worker = RequestWorker(self.api.ask_ai, question)
        self.worker.finished.connect(self.on_ai_loaded)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(lambda _: self.set_loading_state(False))
        self.worker.error.connect(lambda _: self.set_loading_state(False))
        self.worker.start()

    def on_ai_loaded(self, data):
        if data.get("error"):
            self.ai_response.setText(f"❌ Ошибка: {data['error']}")
            return

        data_html = markdown.markdown(data["answer"], extensions=["extra"])
        self.ai_response.setHtml(data_html)

    def show_error(self, error_text):
        QMessageBox.critical(self, "Ошибка", error_text)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #f4f6fb;
                color: #1f2937;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 14px;
            }

            QWidget {
                color: #1f2937;
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 14px;
            }

            QFrame#header {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4f46e5,
                    stop:1 #7c3aed
                );
                border-radius: 24px;
            }

            QLabel#appTitle,
            QLabel#appSubtitle,
            QLabel#statusLabel {
                background: transparent;
                border: none;
            }

            QLabel#appTitle {
                color: white;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#appSubtitle {
                color: rgba(255, 255, 255, 0.88);
                font-size: 13px;
            }

            QLabel#statusLabel {
                color: white;
                font-size: 12px;
                margin-top: 6px;
            }

            QFrame#card {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 22px;
            }

            QLabel#pageTitle {
                background: transparent;
                font-size: 20px;
                font-weight: 700;
                color: #111827;
            }

            QLabel#pageSubtitle,
            QLabel#fieldLabel {
                background: transparent;
            }

            QLabel#pageSubtitle {
                font-size: 13px;
                color: #6b7280;
                margin-bottom: 4px;
            }

            QLabel#fieldLabel {
                font-size: 13px;
                font-weight: 600;
                color: #374151;
                margin-top: 4px;
            }

            QTextEdit#contentBox, QTextEdit#inputBox, QLineEdit, QComboBox {
                background: #f9fafb;
                border: 1px solid #dbe3ee;
                border-radius: 16px;
                padding: 12px;
                color: #111827;
                selection-background-color: #c7d2fe;
            }

            QTextEdit#contentBox {
                font-size: 15px;
                line-height: 1.5;
            }

            QTextEdit#inputBox {
                font-size: 14px;
            }

            QPushButton {
                background: #4f46e5;
                color: white;
                border: none;
                border-radius: 16px;
                padding: 14px 18px;
                font-size: 14px;
                font-weight: 700;
                min-height: 20px;
            }

            QPushButton:hover {
                background: #4338ca;
            }

            QPushButton:pressed {
                background: #3730a3;
            }

            QPushButton:disabled {
                background: #a5b4fc;
                color: white;
            }

            QFrame#bottomNav {
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 22px;
            }

            QPushButton#navButton {
                background: transparent;
                color: #6b7280;
                border: none;
                border-radius: 14px;
                padding: 12px 8px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#navButton:checked {
                background: #eef2ff;
                color: #4338ca;
            }

            QPushButton#navButton:hover {
                background: #f3f4f6;
            }

            QMessageBox {
                background: white;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 6px;
            }

            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 5px;
                min-height: 24px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = ChristianReferenceApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()