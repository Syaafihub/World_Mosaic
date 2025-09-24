from flask import Flask, render_template, request, redirect, jsonify
from database import init_db, add_note, get_notes
from deep_translator import GoogleTranslator

app = Flask(__name__)
init_db()  # Ensure DB is created

@app.route('/')
def index():
    notes = get_notes()
    return render_template("index.html", notes=notes)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        text = request.form['text']
        if text.strip():
            add_note(text)
        return redirect('/')
    return '''
    <form method="POST">
      <textarea name="text" placeholder="Write a note"></textarea>
      <br>
      <button type="submit">Add Note</button>
    </form>
    '''

@app.route('/translate', methods=['POST'])
def translate_notes():
    data = request.get_json()
    indices = data.get("indices", [])
    lang = data.get("lang", "")
    notes = get_notes()
    result = {}
    try:
        for idx, note in enumerate(notes):
            if str(idx) in indices:
                translated = GoogleTranslator(source="auto", target=lang).translate(note["text"])
                result[str(idx)] = translated
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
