import os
import sqlite3
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)


class BibleDatabase:
    def __init__(self):
        self.conn_synodal = sqlite3.connect('synodal.sqlite', check_same_thread=False)
        self.cursor_synodal = self.conn_synodal.cursor()
        
        self.conn_local = sqlite3.connect('chrisitan_texts.db', check_same_thread=False)
        self.cursor_local = self.conn_local.cursor()

        self.create_tables()
        self.populate_initial_data()

        self.book_names = [
            "Бытие", "Исход", "Левит", "Числа", "Второзаконие",
            "Иисус Навин", "Судьи", "Руфь", "1 Царств", "2 Царств",
            "3 Царств", "4 Царств", "1 Паралипоменон", "2 Паралипоменон", "Ездра",
            "Неемия", "Есфирь", "Иов", "Псалтирь", "Притчи",
            "Екклесиаст", "Песнь Песней", "Исаия", "Иеремия", "Плач Иеремии",
            "Иезекииль", "Даниил", "Осия", "Иоиль", "Амос",
            "Авдий", "Иона", "Михей", "Наум", "Аввакум",
            "Софония", "Аггей", "Захария", "Малахия",
            "Матфея", "Марка", "Луки", "Иоанна", "Деяния",
            "Иакова", "1 Петра", "2 Петра", "1 Иоанна", "2 Иоанна",
            "3 Иоанна", "Иуды", "Римлянам", "1 Коринфянам", "2 Коринфянам",
            "Галатам", "Ефесянам", "Филиппийцам", "Колоссянам", "1 Фессалоникийцам",
            "2 Фессалоникийцам", "1 Тимофею", "2 Тимофею", "Титу", "Филимону",
            "Евреям", "Откровение"
        ]

    def create_tables(self):
        self.cursor_local.execute("""
            CREATE TABLE IF NOT EXISTS commandments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                text TEXT,
                reference TEXT
            )
        """)
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
            self.cursor_local.executemany("""
                INSERT INTO commandments (category, text, reference)
                VALUES (?, ?, ?)
            """, initial_commandments)
            self.conn_local.commit()

    def get_random_scripture(self):
        try:
            self.cursor_synodal.execute("""
                SELECT book, chapter, verse, text
                FROM verses
                ORDER BY RANDOM()
                LIMIT 1
            """)
            row = self.cursor_synodal.fetchone()
            if not row:
                return None

            book_num, chapter, verse, text = row
            if not (1 <= book_num <= 66):
                return None

            category = "Ветхий Завет" if book_num <= 39 else "Новый Завет"
            book_name = self.book_names[book_num - 1]

            return {
                "category": category,
                "book": book_name,
                "chapter": chapter,
                "verse": verse,
                "text": text,
                "translation": "Синодальный перевод"
            }
        except Exception as e:
            return {"error": str(e)}

    def get_random_commandment(self, category=None):
        try:
            if category and category != "Все":
                self.cursor_local.execute("""
                    SELECT category, text, reference
                    FROM commandments
                    WHERE category = ?
                    ORDER BY RANDOM()
                    LIMIT 1
                """, (category,))
            else:
                self.cursor_local.execute("""
                    SELECT category, text, reference
                    FROM commandments
                    ORDER BY RANDOM()
                    LIMIT 1
                """)
            row = self.cursor_local.fetchone()
            if not row:
                return None

            cat, text, reference = row
            return {
                "category": cat,
                "text": text,
                "reference": reference
            }
        except Exception as e:
            return {"error": str(e)}

    def search_texts(self, keyword):
        try:
            self.cursor_synodal.execute("""
                SELECT book, chapter, verse, text
                FROM verses
                WHERE text LIKE ?
                LIMIT 10
            """, (f'%{keyword}%',))
            rows = self.cursor_synodal.fetchall()

            results = []
            for book_num, chapter, verse, text in rows:
                if 1 <= book_num <= 66:
                    category = "Ветхий Завет" if book_num <= 39 else "Новый Завет"
                    book_name = self.book_names[book_num - 1]
                    results.append({
                        "category": category,
                        "book": book_name,
                        "chapter": chapter,
                        "verse": verse,
                        "text": text,
                        "translation": "Синодальный перевод"
                    })
            return results
        except Exception as e:
            return {"error": str(e)}


class AIService:
    def __init__(self):
        api_key = os.getenv("BOT_HUB_API_KEY")
        if not api_key:
            raise ValueError("Не задан BOT_HUB_API_KEY")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://bothub.chat/api/v2/openai/v1"
        )
        self.model = "gpt-4.1"
        self.system_prompt = (
            "Ты православный священник и проповедник. "
            "Отвечай на вопросы пользователя вдохновенно, с использованием "
            "библейских цитат, притч и примеров из жизни святых. "
            "Твой язык должен быть живым, образным, но уважительным и назидательным."
        )

    def ask(self, question):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question}
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content


db = BibleDatabase()
ai_service = None

try:
    ai_service = AIService()
except Exception as e:
    print(f"AI сервис не инициализирован: {e}")


@app.route("/scripture/random", methods=["GET"])
def random_scripture():
    return jsonify(db.get_random_scripture())


@app.route("/commandment/random", methods=["GET"])
def random_commandment():
    category = request.args.get("category", "Все")
    return jsonify(db.get_random_commandment(category))


@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword", "").strip()
    if not keyword:
        return jsonify({"error": "keyword is required"}), 400
    return jsonify(db.search_texts(keyword))


@app.route("/ai/ask", methods=["POST"])
def ask_ai():
    if ai_service is None:
        return jsonify({"error": "AI сервис недоступен"}), 500

    data = request.get_json()
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400

    try:
        answer = ai_service.ask(question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)