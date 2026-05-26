const BASE_URL = "http://127.0.0.1:5000";

export async function getRandomScripture() {
  const res = await fetch(`${BASE_URL}/scripture/random`);
  return res.json();
}

export async function getRandomCommandment(category: string = "Все") {
  const res = await fetch(
    `${BASE_URL}/commandment/random?category=${encodeURIComponent(category)}`
  );
  return res.json();
}

export async function searchTexts(keyword: string) {
  const res = await fetch(
    `${BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`
  );
  return res.json();
}

export async function askAI(question: string) {
  const res = await fetch(`${BASE_URL}/ai/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ question })
  });

  return res.json();
}

export async function searchScriptures(keyword: string) {
  const res = await fetch(`${BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`);
  return res.json();
}
