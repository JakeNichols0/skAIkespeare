from flask import redirect, url_for
import flask as fk
from flask import render_template as rt
from html import escape

app = fk.Flask(
  __name__
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)

def load_input(text="",error=""):
  return rt('input.html', text=escape(text), error=escape(error))

@app.route('/', methods = ['GET', 'POST'])
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
  text=escape(fk.request.form['text'])
  return rt("analysis.html", text=text)