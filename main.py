from flask import redirect, url_for
import flask as fk
from flask import render_template as rt
from html import escape

app = fk.Flask(
  __name__
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)

@app.route('/')
def index():
    return rt("input.html")

@app.route('/analysis', methods=['POST'])
def analysis():
  return rt("analysis.html", text=escape(fk.request.form['text']))