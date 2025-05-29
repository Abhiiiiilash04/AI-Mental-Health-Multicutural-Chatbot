from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai
import os
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from datetime import datetime

app = Flask(__name__)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Language detection
def get_lang_detector(nlp, name):
    return LanguageDetector()

nlp = spacy.load("en_core_web_sm")
Language.factory("language_detector", func=get_lang_detector)
nlp.add_pipe('language_detector', last=True)

# Log file
LOG_FILE = "chat_log.txt"

def detect_language(text):
    doc = nlp(text)
    return doc._.language["language"]

def get_gpt_response(prompt, lang="en"):
    if lang == "hi":
        system_prompt = (
            "आप ZenMate हैं, एक सहानुभूतिपूर्ण मानसिक स्वास्थ्य सहायक जो भारत के सांस्कृतिक मूल्यों, पारिवारिक संरचना, "
            "और सामाजिक दबावों को समझते हैं। कृपया व्यक्ति की भावनाओं को ध्यान में रखते हुए, करुणा और समझदारी के साथ उत्तर दें।"
        )
    elif lang == "ta":
        system_prompt = (
            "நீங்கள் ZenMate, தமிழ் மக்களின் பாரம்பரியம், குடும்ப உறவுகள் மற்றும் சமூக மனநிலைகளை புரிந்து கொள்ளக்கூடிய, "
            "ஒரு கனிவான மற்றும் கலாச்சார விழிப்புணர்வுள்ள மனநல ஆலோசகர். தயவுடன் மற்றும் பரிவுடன் பதிலளிக்கவும்."
        )
    else:
        system_prompt = (
            "You are ZenMate, an empathetic mental health assistant who understands Western culture, individualism, "
            "and emotional expression. Respond kindly and insightfully with cultural sensitivity."
        )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def log_interaction(user_input, bot_response):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
        f.write(f"User: {user_input}\n")
        f.write(f"ZenMate: {bot_response}\n")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    lang = detect_language(user_input)
    response = get_gpt_response(user_input, lang)
    log_interaction(user_input, response)

    # ✅ Debug prints
    print("User:", user_input)
    print("Lang:", lang)
    print("Response:", response)

    return jsonify({"response": response})

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/admin/log")
def admin_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "No logs available."

if __name__ == "__main__":
    app.run(debug=True)
