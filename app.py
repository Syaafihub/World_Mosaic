from flask import Flask, render_template, request, redirect, url_for, jsonify
from better_profanity import profanity
from googletrans import Translator

app = Flask(__name__)
profanity.load_censor_words()
translator = Translator()

notes = []  # In-memory list of notes

@app.route("/")
def index():
    return render_template("index.html", notes=notes)

@app.route("/add_note", methods=["POST"])
def add_note():
    content = request.form.get("content")
    if not content:
        return redirect(url_for("index"))
    content = profanity.censor(content)
    notes.append({"content": content})
    return redirect(url_for("index"))

@app.route("/translate/<int:note_id>/<lang>")
def translate_note(note_id, lang):
    if 0 <= note_id < len(notes):
        original = notes[note_id]["content"]
        translated = translator.translate(original, dest=lang).text
        return jsonify({"translated": translated})
    return jsonify({"translated": ""})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
