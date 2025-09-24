from flask import Flask, render_template, request, redirect, url_for, jsonify
from better_profanity import profanity
from googletrans import Translator

app = Flask(__name__)
profanity.load_censor_words()
translator = Translator()

notes = []  # Each note: {"text": original, "translations": {}}
MAX_CHARS = 50

@app.route("/")
def index():
    focus = request.args.get("focus", default=None, type=int)
    return render_template("index.html", notes=notes, focus=focus)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    global notes
    if request.method == "POST":
        text = request.form.get("note", "").strip()
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS]
        if text:
            if profanity.contains_profanity(text):
                text = "[Inappropriate content removed]"
            notes.append({"text": text, "translations": {}})
            new_index = len(notes) - 1
            return redirect(url_for("index", focus=new_index))
        else:
            return redirect(url_for("index"))
    return render_template("submit.html", max_chars=MAX_CHARS)

@app.route("/reset", methods=["POST"])
def reset():
    global notes
    notes = []
    return redirect(url_for("index"))

@app.route("/translate", methods=["POST"])
def translate_note():
    """
    Translate one or multiple notes.
    Expected JSON: {"indices": [0,1,2], "lang": "es"} for batch translation
    """
    data = request.json
    indices = data.get("indices")
    lang = data.get("lang")
    if indices is None or not lang:
        return jsonify({"error": "Missing parameters"}), 400

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
                note["translations"][lang] = translated_text
                results[idx] = translated_text
            except Exception:
                results[idx] = "[Translation error]"
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
