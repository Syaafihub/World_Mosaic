from flask import Flask, render_template, request, redirect, url_for, jsonify
from better_profanity import profanity
from googletrans import Translator
from pymongo import MongoClient

app = Flask(__name__)
profanity.load_censor_words()
translator = Translator()

# Connect to MongoDB Atlas (replace <URI> with your connection string)
client = MongoClient("mongodb+srv://Syaafi:<db_password>@cluster0.mlvkiin.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.world_mosaic
notes_collection = db.notes

MAX_CHARS = 50

@app.route("/")
def index():
    focus = request.args.get("focus", default=None, type=int)
    notes = list(notes_collection.find())
    return render_template("index.html", notes=notes, focus=focus)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        text = request.form.get("note", "").strip()
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
        if text:
            if profanity.contains_profanity(text):
                text = "[Inappropriate content removed]"
            note = {"text": text, "translations": {}}
            notes_collection.insert_one(note)
            new_index = notes_collection.count_documents({}) - 1
            return redirect(url_for("index", focus=new_index))
        else:
            return redirect(url_for("index"))
    return render_template("submit.html", max_chars=MAX_CHARS)

@app.route("/reset", methods=["POST"])
def reset():
    notes_collection.delete_many({})
    return redirect(url_for("index"))

@app.route("/translate", methods=["POST"])
def translate_note():
    data = request.json
    indices = data.get("indices")
    lang = data.get("lang")
    if indices is None or not lang:
        return jsonify({"error": "Missing parameters"}), 400

    notes = list(notes_collection.find())
    results = {}
    for idx in indices:
        try:
            note = notes[int(idx)]
        except (IndexError, ValueError):
            continue
        if lang in note["translations"]:
            results[idx] = note["translations"][lang]
        else:
            try:
                translated_text = translator.translate(note["text"], dest=lang).text
                notes_collection.update_one(
                    {"_id": note["_id"]},
                    {"$set": {f"translations.{lang}": translated_text}}
                )
                results[idx] = translated_text
            except Exception:
                results[idx] = "[Translation error]"
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
