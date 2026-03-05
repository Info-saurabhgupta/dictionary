import sqlite3
import requests
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
DATABASE = "dictionary.db"

# ---------------- HINDI DATABASE ----------------
def query_hindi(word):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT hi FROM dictionary WHERE en=?", (word.lower(),))
    results = cursor.fetchall()
    conn.close()
    return [r[0] for r in results]

# ---------------- TRANSLATE EXAMPLE ----------------
def translate_to_hindi(text):
    try:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|hi"
        response = requests.get(url)
        data = response.json()
        return data["responseData"]["translatedText"]
    except:
        return ""

# ---------------- ENGLISH API ----------------
def query_english_api(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()[0]

    phonetic = ""
    uk_audio = ""
    us_audio = ""

    for p in data.get("phonetics", []):
        if not phonetic and p.get("text"):
            phonetic = p.get("text")

        audio = p.get("audio", "")
        if audio:
            if "us" in audio.lower():
                us_audio = audio
            elif "uk" in audio.lower():
                uk_audio = audio
            elif not uk_audio:
                uk_audio = audio

    meanings = data.get("meanings", [])

    # Translate examples
    for m in meanings:
        for d in m["definitions"]:
            if "example" in d:
                d["example_hi"] = translate_to_hindi(d["example"])

    return {
        "phonetic": phonetic,
        "uk_audio": uk_audio,
        "us_audio": us_audio,
        "meanings": meanings
    }

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    word = request.args.get("word", "")
    hindi = query_hindi(word)
    english = query_english_api(word)

    return jsonify({
        "word": word,
        "hindi": hindi,
        "english": english
    })

# ---------------- SUGGESTION ----------------
@app.route("/suggest")
def suggest():
    term = request.args.get("term", "")
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT en FROM dictionary WHERE en LIKE ? LIMIT 8",
        (term.lower() + "%",)
    )

    results = cursor.fetchall()
    conn.close()

    words = [r[0] for r in results]
    return jsonify(words)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))