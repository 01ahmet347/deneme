from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
from datetime import datetime
import json
import os

app = Flask(__name__)

# Kullanıcı bilgileri
user_data = {
    "name": "",
    "start_time": None,
    "end_time": None,
    "score": 0,
    "selected_language": "",
    "detailed_answers": [],
    "total_attempts": 0,
    "correct_attempts": 0
}

# Skor tablosu dosyası
SCOREBOARD_FILE = "scoreboard.json"

# Sorular ve cevaplar
questions = {
    "Python": [
        ("Python'da bir listeyi sıralamak için hangi fonksiyon kullanılır?", "sorted"),
        ("Python'da bir değişkeni hangi anahtar kelimeyle global olarak tanımlarsınız?", "global"),
        ("Python'da bir sözlük nasıl tanımlanır?", "dict")
    ],
    "JavaScript": [
        ("JavaScript'te bir değişkeni tanımlamak için hangi anahtar kelimeler kullanılır?", "var, let, const"),
        ("JavaScript hangi dil türüne aittir?", "dinamik"),
        ("JavaScript'te DOM neyi ifade eder?", "Document Object Model")
    ]
}

# Skor tablosunu yükleme ve kaydetme
def load_scoreboard():
    try:
        if os.path.exists(SCOREBOARD_FILE):
            with open(SCOREBOARD_FILE, "r") as f:
                return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return []

def save_scoreboard(scoreboard):
    with open(SCOREBOARD_FILE, "w") as f:
        json.dump(scoreboard, f, indent=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    data = request.form
    user_data["name"] = data.get("name")
    user_data["selected_language"] = data.get("language")
    user_data["start_time"] = datetime.now().isoformat()

    if user_data["selected_language"] not in questions:
        return redirect(url_for('home'))

    user_data["questions"] = random.sample(questions[user_data["selected_language"]], 3)
    user_data["current_question"] = 0
    user_data["score"] = 0

    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        answer = request.form.get("answer").strip().lower()
        correct_answer = user_data["questions"][user_data["current_question"]][1].lower()

        if answer == correct_answer:
            user_data["score"] += 1

        user_data["current_question"] += 1

        if user_data["current_question"] >= len(user_data["questions"]):
            return redirect(url_for('result'))

    question = user_data["questions"][user_data["current_question"]][0]
    return render_template('quiz.html', question=question, current=user_data["current_question"] + 1, total=len(user_data["questions"]))

@app.route('/result')
def result():
    end_time = datetime.now()
    user_data["end_time"] = end_time.isoformat()

    scoreboard = load_scoreboard()
    scoreboard.append({
        "name": user_data["name"],
        "score": user_data["score"],
        "language": user_data["selected_language"],
        "time": (end_time - datetime.fromisoformat(user_data["start_time"])).seconds
    })
    save_scoreboard(scoreboard)

    return render_template('result.html', score=user_data["score"], total=len(user_data["questions"]))

@app.route('/scoreboard')
def scoreboard():
    scores = load_scoreboard()
    return render_template('scoreboard.html', scores=scores)

if __name__ == '__main__':
    app.run(debug=True)
