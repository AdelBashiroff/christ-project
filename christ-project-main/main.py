import sys
import random
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QTextEdit, QComboBox,
                             QLabel, QMessageBox, QTabWidget, QLineEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from openai import OpenAI


# База данных: synodal.sqlite для текстов, christian_texts.db для заповедей
class BibleDatabase:
    def __init__(self):
        # Подключение к synodal.sqlite (синодальный перевод)
        self.conn_synodal = sqlite3.connect('synodal.sqlite')
        self.cursor_synodal = self.conn_synodal.cursor()

        # Подключение к christian_texts.db (заповеди и старые данные)
        self.conn_local = sqlite3.connect('christian_texts.db')
        self.cursor_local = self.conn_local.cursor()

        # Создаём таблицы для заповедей, если их нет
        self.create_tables()
        self.populate_initial_data()

        # Список названий книг синодального перевода (66 книг)
        self.book_names = [
            # Ветхий Завет (1-39)
            "Бытие", "Исход", "Левит", "Числа", "Второзаконие",
            "Иисус Навин", "Судьи", "Руфь", "1 Царств", "2 Царств",
            "3 Царств", "4 Царств", "1 Паралипоменон", "2 Паралипоменон", "Ездра",
            "Неемия", "Есфирь", "Иов", "Псалтирь", "Притчи",
            "Екклесиаст", "Песнь Песней", "Исаия", "Иеремия", "Плач Иеремии",
            "Иезекииль", "Даниил", "Осия", "Иоиль", "Амос",
            "Авдий", "Иона", "Михей", "Наум", "Аввакум",
            "Софония", "Аггей", "Захария", "Малахия",
            # Новый Завет (40-66)
            "Матфея", "Марка", "Луки", "Иоанна", "Деяния",
            "Иакова", "1 Петра", "2 Петра", "1 Иоанна", "2 Иоанна",
            "3 Иоанна", "Иуды", "Римлянам", "1 Коринфянам", "2 Коринфянам",
            "Галатам", "Ефесянам", "Филиппийцам", "Колоссянам", "1 Фессалоникийцам",
            "2 Фессалоникийцам", "1 Тимофею", "2 Тимофею", "Титу", "Филимону",
            "Евреям", "Откровение"
        ]

    def create_tables(self):
        # Таблица для заповедей (только в локальной БД)
        self.cursor_local.execute('''
            CREATE TABLE IF NOT EXISTS commandments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                text TEXT,
                reference TEXT
            )
        ''')
        self.conn_local.commit()

    def populate_initial_data(self):
        self.cursor_local.execute("SELECT COUNT(*) FROM commandments")
        if self.cursor_local.fetchone()[0] == 0:
            initial_commandments = [
                ('Десять заповедей', 'Не убивай.', 'Исход 20:13'),
                ('Десять заповедей', 'Не прелюбодействуй.', 'Исход 20:14'),
                ('Десять заповедей', 'Не кради.', 'Исход 20:15'),
                ('Десять заповедей', 'Не произноси ложного свидетельства на ближнего твоего.', 'Исход 20:16'),
                ('Заповеди Иисуса', 'Любите врагов ваших, благословляйте проклинающих вас.', 'Матфея 5:44'),
                ('Заповеди Иисуса', 'Итак во всем, как хотите, чтобы с вами поступали люди, так поступайте и вы с ними.', 'Матфея 7:12'),
            ]

            for cmd in initial_commandments:
                self.cursor_local.execute('''
                    INSERT INTO commandments (category, text, reference)
                    VALUES (?, ?, ?)
                ''', cmd)
            self.conn_local.commit()

    def get_random_scripture(self):
        try:
            # Предполагается, что таблица называется "bible" с полями:
            # book (INT), chapter (INT), verse (INT), text (TEXT)
            # Если имя таблицы другое, замените "bible" ниже.
            self.cursor_synodal.execute('''
                SELECT book, chapter, verse, text FROM verses ORDER BY RANDOM() LIMIT 1
            ''')
            row = self.cursor_synodal.fetchone()
            if not row:
                return None

            book_num, chapter, verse, text = row
            # Проверяем, что номер книги в допустимом диапазоне (1-66)
            if not (1 <= book_num <= 66):
                return None

            category = "Ветхий Завет" if book_num <= 39 else "Новый Завет"
            book_name = self.book_names[book_num - 1]
            return (category, book_name, chapter, verse, text, "Синодальный перевод")
        except Exception as e:
            print(f"Ошибка при получении случайного писания: {e}")
            return None

    def get_random_commandment(self):
        self.cursor_local.execute('''
            SELECT category, text, reference 
            FROM commandments ORDER BY RANDOM() LIMIT 1
        ''')
        return self.cursor_local.fetchone()

    def search_texts(self, keyword):
        try:
            self.cursor_synodal.execute('''
                SELECT book, chapter, verse, text FROM verses 
                WHERE text LIKE ? LIMIT 10
            ''', (f'%{keyword}%',))
            rows = self.cursor_synodal.fetchall()

            results = []
            for book_num, chapter, verse, text in rows:
                if 1 <= book_num <= 66:
                    category = "Ветхий Завет" if book_num <= 39 else "Новый Завет"
                    book_name = self.book_names[book_num - 1]
                    results.append((category, book_name, chapter, verse, text, "Синодальный перевод"))
            return results
        except Exception as e:
            print(f"Ошибка при поиске: {e}")
            return []

    def close(self):
        self.conn_synodal.close()
        self.conn_local.close()


class AIWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, messages, api_key, model="gpt-4.1"):
        super().__init__()
        self.messages = messages
        self.api_key = api_key
        self.model = model

    def run(self):
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://bothub.chat/api/v2/openai/v1"
        )
        chat_completion = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.7
        )
        assistant_text = chat_completion.choices[0].message.content
        self.finished.emit(assistant_text)


# Главное окно приложения
class ChristianReferenceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = BibleDatabase()
        self.ai_worker = None
        self.api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjM5YjVkN2UwLTZjNTYtNDRhMi1iMGI3LTM2MjBlZTEwODg5NSIsImlzRGV2ZWxvcGVyIjp0cnVlLCJpYXQiOjE3NzM3NTI4MDMsImV4cCI6MjA4OTMyODgwMywianRpIjoib29LV3dZZ2xObzF0VG1QcCJ9.mSxofFHo7fH5Vyfb78uJYlt-lCMnPQ_cBWyKLIXWRO8"
        self.model = "gpt-4.1"
        self.messages = [
            {"role": "system", "content": "Ты православный священник и проповедник. "
            "Отвечай на вопросы пользователя вдохновенно, с использованием библейских цитат, притч и примеров из жизни святых. "
            "Твой язык должен быть живым, образным, но при этом уважительным и назидательным. "
            "Избегай сухих, формальных ответов, как у обычного чат бота. "
            "Говори как пастырь, который наставляет свою паству."}
        ]
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Справочник священника - Христианские писания")
        self.setGeometry(100, 100, 800, 600)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        random_tab = QWidget()
        tabs.addTab(random_tab, "Случайные писания")
        self.setup_random_tab(random_tab)

        commandments_tab = QWidget()
        tabs.addTab(commandments_tab, "Заповеди")
        self.setup_commandments_tab(commandments_tab)

        search_tab = QWidget()
        tabs.addTab(search_tab, "Поиск")
        self.setup_search_tab(search_tab)

        ai_tab = QWidget()
        tabs.addTab(ai_tab, "AI помощник")
        self.setup_ai_tab(ai_tab)

        self.apply_styles()

    def setup_random_tab(self, tab):
        layout = QVBoxLayout()
        title = QLabel("Случайное писание дня")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.scripture_display = QTextEdit()
        self.scripture_display.setReadOnly(True)
        self.scripture_display.setFont(QFont("Times", 14))
        layout.addWidget(self.scripture_display)

        btn_layout = QHBoxLayout()
        generate_btn = QPushButton("Получить случайное писание")
        generate_btn.clicked.connect(self.generate_random_scripture)
        btn_layout.addWidget(generate_btn)

        layout.addLayout(btn_layout)
        tab.setLayout(layout)

    def setup_commandments_tab(self, tab):
        layout = QVBoxLayout()
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Категория:"))

        self.cmd_category = QComboBox()
        self.cmd_category.addItems(["Все", "Десять заповедей", "Заповеди Иисуса"])
        category_layout.addWidget(self.cmd_category)

        layout.addLayout(category_layout)

        self.commandments_display = QTextEdit()
        self.commandments_display.setReadOnly(True)
        self.commandments_display.setFont(QFont("Times", 14))
        layout.addWidget(self.commandments_display)

        get_cmd_btn = QPushButton("Получить заповедь")
        get_cmd_btn.clicked.connect(self.get_commandment)
        layout.addWidget(get_cmd_btn)

        tab.setLayout(layout)

    def setup_search_tab(self, tab):
        layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Поиск:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите ключевое слово...")
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        self.search_results = QTextEdit()
        self.search_results.setReadOnly(True)
        self.search_results.setFont(QFont("Times", 12))
        layout.addWidget(self.search_results)

        tab.setLayout(layout)

    def setup_ai_tab(self, tab):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Задайте вопрос священнику:"))

        self.ai_input = QTextEdit()
        self.ai_input.setMaximumHeight(100)
        self.ai_input.setPlaceholderText("Например: Расскажи о любви в христианстве...")
        layout.addWidget(self.ai_input)

        ask_btn = QPushButton("Спросить AI")
        ask_btn.clicked.connect(self.ask_ai)
        layout.addWidget(ask_btn)

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
            self.scripture_display.setText(display_text)
        else:
            self.scripture_display.setText(
                "Не удалось получить писание. Проверьте:\n"
                "- наличие файла synodal.sqlite в папке с программой;\n"
                "- имя таблицы (в коде используется 'bible');\n"
                "- структуру таблицы (поля book, chapter, verse, text)."
            )

    def get_commandment(self):
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
            for i, res in enumerate(results, 1):
                category, book, chapter, verse, text, explanation = res
                display_text += f"{i}. {book} {chapter}:{verse}\n"
                display_text += f"   \"{text[:100]}...\"\n\n"
            self.search_results.setText(display_text)
        else:
            self.search_results.setText("Ничего не найдено (или ошибка при поиске).")

    def ask_ai(self):
        question = self.ai_input.toPlainText().strip()
        if not question:
            QMessageBox.warning(self, "Предупреждение", "Введите вопрос")
            return

        if not self.api_key:
            self.ai_response.setText("⚠️ API ключ не настроен.")
            return

        messages_to_send = self.messages.copy()
        messages_to_send.append({"role": "user", "content": question})

        self.ai_response.setText("⏳ Ожидайте, проповедник божий думает над ответом...")

        self.ai_worker = AIWorker(messages_to_send, self.api_key, self.model)
        self.ai_worker.finished.connect(self.on_ai_response)
        self.ai_worker.error.connect(self.on_ai_error)
        self.ai_worker.start()

    def on_ai_response(self, response):
        self.ai_response.setText(response)
        self.messages.append({"role": "assistant", "content": response})

    def on_ai_error(self, error_msg):
        self.ai_response.setText(f"❌ Ошибка: {error_msg}")

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QTabWidget::pane { border: 1px solid #cccccc; background-color: white; }
            QTabBar::tab { background-color: #e0e0e0; color: black; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background-color: white; color: black; border-bottom: 2px solid #4a90e2; }
            QPushButton { background-color: #4a90e2; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #357abd; }
            QTextEdit { border: 1px solid #cccccc; border-radius: 4px; padding: 8px; background-color: white; color: black; selection-background-color: #4a90e2; selection-color: white; }
            QLineEdit { border: 1px solid #cccccc; border-radius: 4px; padding: 6px; background-color: white; color: black; }
            QComboBox { border: 1px solid #cccccc; border-radius: 4px; padding: 4px; background-color: white; color: black; }
            QComboBox QAbstractItemView { background-color: white; color: black; selection-background-color: #4a90e2; selection-color: white; }
            QLabel { color: black; }
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