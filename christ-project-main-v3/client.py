import requests


class ApiClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url.rstrip("/")

    def get_random_scripture(self):
        response = requests.get(f"{self.base_url}/scripture/random", timeout=10)
        response.raise_for_status()
        return response.json()

    def get_random_commandment(self, category="Все"):
        response = requests.get(
            f"{self.base_url}/commandment/random",
            params={"category": category},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def search_texts(self, keyword):
        response = requests.get(
            f"{self.base_url}/search",
            params={"keyword": keyword},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def ask_ai(self, question):
        response = requests.post(
            f"{self.base_url}/ai/ask",
            json={"question": question},
            timeout=60
        )
        response.raise_for_status()
        return response.json()