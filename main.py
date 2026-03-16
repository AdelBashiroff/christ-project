import sys
import random
import sqlite3
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QComboBox,
                             QLabel, QMessageBox, QTabWidget, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import requests


# База данных христианских текстов
class BibleDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('christian_texts.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.populate_initial_data()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS texts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                book TEXT,
                chapter INTEGER,
                verse INTEGER,
                text TEXT,
                explanation TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commandments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                text TEXT,
                reference TEXT
            )
        ''')
        self.conn.commit()

    def populate_initial_data(self):
        # Проверяем, есть ли уже данные
        self.cursor.execute("SELECT COUNT(*) FROM texts")
        if self.cursor.fetchone()[0] == 0:
            initial_texts = [
                ('Ветхий Завет', 'Бытие', 1, 1, 'В начале сотворил Бог небо и землю.', 'Начало творения мира'),
                ('Ветхий Завет', 'Псалтирь', 22, 1, 'Господь - Пастырь мой; я ни в чем не буду нуждаться.',
                 'Господь заботится о нас'),
                ('Новый Завет', 'От Иоанна', 3, 16,
                 'Ибо так возлюбил Бог мир, что отдал Сына Своего Единородного, дабы всякий верующий в Него, не погиб, но имел жизнь вечную.',
                 'Любовь Бога к людям'),
                ('Ветхий Завет', 'Исход', 20, 3, 'Да не будет у тебя других богов пред лицем Моим.', 'Первая заповедь'),
                ('Новый Завет', 'От Матфея', 5, 3, 'Блаженны нищие духом, ибо их есть Царство Небесное.',
                 'Нагорная проповедь'),
                ('Новый Завет', 'От Матфея', 22, 37,
                 'Возлюби Господа Бога твоего всем сердцем твоим и всею душею твоею и всем разумением твоим.',
                 'Великая заповедь'),
            ]

            for text in initial_texts:
                self.cursor.execute('''
                    INSERT INTO texts (category, book, chapter, verse, text, explanation)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', text)

            initial_commandments = [
                ('Десять заповедей', 'Не убивай.', 'Исход 20:13'),
                ('Десять заповедей', 'Не прелюбодействуй.', 'Исход 20:14'),
                ('Десять заповедей', 'Не кради.', 'Исход 20:15'),
                ('Десять заповедей', 'Не произноси ложного свидетельства на ближнего твоего.', 'Исход 20:16'),
                ('Заповеди Иисуса', 'Любите врагов ваших, благословляйте проклинающих вас.', 'Матфея 5:44'),
                (
                'Заповеди Иисуса', 'Итак во всем, как хотите, чтобы с вами поступали люди, так поступайте и вы с ними.',
                'Матфея 7:12'),
            ]

            for cmd in initial_commandments:
                self.cursor.execute('''
                    INSERT INTO commandments (category, text, reference)
                    VALUES (?, ?, ?)
                ''', cmd)

            self.conn.commit()

    def get_random_scripture(self):
        self.cursor.execute('''
            SELECT category, book, chapter, verse, text, explanation 
            FROM texts ORDER BY RANDOM() LIMIT 1
        ''')
        return self.cursor.fetchone()

    def get_random_commandment(self):
        self.cursor.execute('''
            SELECT category, text, reference 
            FROM commandments ORDER BY RANDOM() LIMIT 1
        ''')
        return self.cursor.fetchone()

    def search_texts(self, keyword):
        self.cursor.execute('''
            SELECT category, book, chapter, verse, text, explanation 
            FROM texts WHERE text LIKE ? OR explanation LIKE ?
            LIMIT 10
        ''', (f'%{keyword}%', f'%{keyword}%'))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


# Замените AIWorker в коде на этот вариант
class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            # Используем бесплатный API (например, через RapidAPI)
            import requests

            # Пример с бесплатным API (может быть медленнее)
            response = requests.post(
                'https://open-ai21.p.rapidapi.com/chatgpt',
                headers={
                    'x-rapidapi-key': 'ваш_ключ_rapidapi',  # Получите на rapidapi.com
                    'x-rapidapi-host': 'open-ai21.p.rapidapi.com',
                    'Content-Type': 'application/json'
                },
                json={
                    'messages': [
                        {'role': 'user', 'content': self.prompt}
                    ],
                    'temperature': 0.7
                }
            )

            if response.status_code == 200:
                result = response.json()
                self.finished.emit(result.get('result', 'Нет ответа'))
            else:
                self.error.emit("Ошибка API")

        except Exception as e:
            self.error.emit(str(e))


# Главное окно приложения
class ChristianReferenceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = BibleDatabase()
        self.ai_worker = None
        self.api_key = ""  # Введите ваш API ключ OpenAI
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Справочник священника - Христианские писания")
        self.setGeometry(100, 100, 800, 600)

        # Создаем вкладки
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Вкладка случайных писаний
        random_tab = QWidget()
        tabs.addTab(random_tab, "Случайные писания")
        self.setup_random_tab(random_tab)

        # Вкладка заповедей
        commandments_tab = QWidget()
        tabs.addTab(commandments_tab, "Заповеди")
        self.setup_commandments_tab(commandments_tab)

        # Вкладка поиска
        search_tab = QWidget()
        tabs.addTab(search_tab, "Поиск")
        self.setup_search_tab(search_tab)

        # Вкладка AI генерации
        ai_tab = QWidget()
        tabs.addTab(ai_tab, "AI помощник")
        self.setup_ai_tab(ai_tab)

        # Применяем стили
        self.apply_styles()

    def setup_random_tab(self, tab):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Случайное писание дня")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Текстовое поле для отображения
        self.scripture_display = QTextEdit()
        self.scripture_display.setReadOnly(True)
        self.scripture_display.setFont(QFont("Times", 14))
        layout.addWidget(self.scripture_display)

        # Кнопка генерации
        btn_layout = QHBoxLayout()
        generate_btn = QPushButton("Получить случайное писание")
        generate_btn.clicked.connect(self.generate_random_scripture)
        btn_layout.addWidget(generate_btn)

        layout.addLayout(btn_layout)
        tab.setLayout(layout)

    def setup_commandments_tab(self, tab):
        layout = QVBoxLayout()

        # Выбор категории заповедей
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Категория:"))

        self.cmd_category = QComboBox()
        self.cmd_category.addItems(["Все", "Десять заповедей", "Заповеди Иисуса"])
        category_layout.addWidget(self.cmd_category)

        layout.addLayout(category_layout)

        # Текстовое поле для заповедей
        self.commandments_display = QTextEdit()
        self.commandments_display.setReadOnly(True)
        self.commandments_display.setFont(QFont("Times", 14))
        layout.addWidget(self.commandments_display)

        # Кнопка получения заповеди
        get_cmd_btn = QPushButton("Получить заповедь")
        get_cmd_btn.clicked.connect(self.get_commandment)
        layout.addWidget(get_cmd_btn)

        tab.setLayout(layout)

    def setup_search_tab(self, tab):
        layout = QVBoxLayout()

        # Поисковая строка
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ключевое слово...")
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Результаты поиска
        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        self.search_results.setFont(QFont("Times", 12))
        layout.addWidget(self.search_results)

        tab.setLayout(layout)

    def setup_ai_tab(self, tab):
        layout = QVBoxLayout()

        # Поле ввода запроса
        layout.addWidget(QLabel("Задайте вопрос священнику:"))

        self.ai_input = QTextEdit()
        self.ai_input.setMaximumHeight(100)
        self.ai_input.setPlaceholderText("Например: Расскажи о любви в христианстве...")
        layout.addWidget(self.ai_input)

        # Кнопка отправки
        ask_btn = QPushButton("Спросить AI")
        ask_btn.clicked.connect(self.ask_ai)
        layout.addWidget(ask_btn)

        # Ответ AI
        layout.addWidget(QLabel("Ответ:"))
        self.ai_response = QTextEdit()
        self.ai_response.setReadOnly(True)
        self.ai_response.setFont(QFont("Times", 12))
        layout.addWidget(self.ai_response)

        tab.setLayout(layout)

    def generate_random_scripture(self):
        scripture = self.db.get_random_scripture()
        if scripture:
            category, book, chapter, verse, text, explanation = scripture
            display_text = f"📖 {book} {chapter}:{verse}\n\n"
            display_text += f"\"{text}\"\n\n"
            display_text += f"📝 Категория: {category}\n"
            display_text += f"💭 Пояснение: {explanation}"
            self.scripture_display.setText(display_text)

    def get_commandment(self):
        category = self.cmd_category.currentText()

        if category == "Все":
            commandment = self.db.get_random_commandment()
        else:
            # Здесь можно добавить фильтрацию по категории
            commandment = self.db.get_random_commandment()

        if commandment:
            cat, text, reference = commandment
            display_text = f"⚖️ Заповедь:\n\n\"{text}\"\n\n"
            display_text += f"📚 Источник: {reference}\n"
            display_text += f"📌 Категория: {cat}"
            self.commandments_display.setText(display_text)

    def perform_search(self):
        keyword = self.search_input.text()
        if not keyword:
            QMessageBox.warning(self, "Предупреждение", "Введите ключевое слово для поиска")
            return

        results = self.db.search_texts(keyword)

        if results:
            display_text = f"Найдено {len(results)} результатов:\n\n"
            for i, result in enumerate(results, 1):
                category, book, chapter, verse, text, explanation = result
                display_text += f"{i}. {book} {chapter}:{verse}\n"
                display_text += f"   \"{text[:100]}...\"\n\n"
            self.search_results.setText(display_text)
        else:
            self.search_results.setText("Ничего не найдено")

    def ask_ai(self):
        question = self.ai_input.toPlainText()
        if not question:
            QMessageBox.warning(self, "Предупреждение", "Введите вопрос")
            return

        if not self.api_key:
            self.ai_response.setText("⚠️ API ключ не настроен. Пожалуйста, добавьте ваш OpenAI API ключ в код.")
            return

        self.ai_response.setText("⏳ Ожидайте ответа от AI...")

        # Запускаем AI в отдельном потоке
        self.ai_worker = AIWorker(question, self.api_key)
        self.ai_worker.finished.connect(self.on_ai_response)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_response(self, response):
        self.ai_response.setText(response)

    def on_ai_error(self, error_msg):
        self.ai_response.setText(f"❌ {error_msg}")

    def apply_styles(self):
        # Устанавливаем светлую тему явно
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: black;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: black;
                border-bottom: 2px solid #4a90e2;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: black;  /* явно устанавливаем черный текст */
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                color: black;  /* явно устанавливаем черный текст */
            }
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
                color: black;  /* явно устанавливаем черный текст */
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #4a90e2;
                selection-color: white;
            }
            QLabel {
                color: black;  /* явно устанавливаем черный текст */
            }
        """)

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ChristianReferenceApp()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
