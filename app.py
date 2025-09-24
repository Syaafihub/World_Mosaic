from flask import Flask, render_template, request, redirect, url_for, jsonify
from deep_translator import GoogleTranslator

app = Flask(__name__)

# In-memory notes list
notes = []

@app.route("/")
def home():
    return render_template("index.html", notes=notes)

@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        text = request.form.get("note")
        if text:
            notes.append({"text": text})
        return redirect(url_for("home"))
    return render_template("submit.html")

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    indices = data.get("indices", [])
    lang = data.get("lang")
    translations = {}

    if lang and indices:
        for idx in indices:
            try:
                idx = int(idx)
                if 0 <= idx < len(notes):
                    original = notes[idx]["text"]
                    translated = GoogleTranslator(source="auto", target=lang).translate(original)
                    translations[idx] = translated
            except Exception as e:
                translations[idx] = f"[Error translating: {e}]"

    return jsonify(translations)

if __name__ == "__main__":
    app.run(debug=True)
