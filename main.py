from flask import redirect, url_for
import flask as fk
from flask import render_template as rt
from html import escape
import pickle

app = fk.Flask(__name__)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)


def load_input(text="", error=""):
  return rt('input.html', text=escape(text), error=escape(error))


def check_line(line):
  #metaphors
  loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
  vectorizer = pickle.load(open('vectorizer.sav', 'rb'))
  
  modelAns = loaded_model.predict(vectorizer.transform([line]))
  print(modelAns)
  return modelAns
  


@app.route('/', methods=['GET', 'POST'])
def index():
  method = fk.request.method
  if method == 'POST':
    text = fk.request.form['text']
    if not text:
      return load_input(text, "No text entered")
    else:
      return redirect(url_for('analysis'), 308)
  return load_input()


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
  text = fk.request.form['text']
  textSplit = text.splitlines()
  lines = []
  for line in textSplit:
    color = ""
    match check_line(line):
      case 1:
        color = "lightgreen"
      case 2:
        color = "lightblue"
      case _:
        color = "None"
    lines.append([line, color])
  return rt("analysis.html", text_in=text, lines=lines)


@app.route('/login', methods=['GET', 'POST'])
def login():
  return rt("login.html")