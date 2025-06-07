from flask import redirect, url_for
import flask as fk
from flask import render_template as rt
from html import escape
import pickle
import sqlite3
import hmac
#import requests

app = fk.Flask(__name__)


def load_input(text="", error="", texts=[]):
  return rt('input.html', text=escape(text), error=escape(error), texts=texts)


def check_line(line):
  metaphorAccuracy = 0
  character = 0
  imagery = 0
  juxtAccuracy = 0
  #metaphors
  loaded_model = pickle.load(open('finalized_model.sav', 'rb'))
  vectorizer = pickle.load(open('vectorizer.sav', 'rb'))

  modelAnsMetaphor = loaded_model.predict_proba(vectorizer.transform([line]))

  if modelAnsMetaphor[0][1] > modelAnsMetaphor[0][0]:
    metaphor_Answer = 1
    metaphorAccuracy = modelAnsMetaphor[0][1]
  else:
    metaphor_Answer = 0
    metaphorAccuracy = modelAnsMetaphor[0][0]

  #characterization
  loaded_model = pickle.load(open('characterizeModel.sav', 'rb'))
  vectorizer = pickle.load(open('characterizeVectorizer.sav', 'rb'))

  modelAnsCharac = loaded_model.predict_proba(vectorizer.transform([line]))
  if modelAnsCharac[0][1] > modelAnsCharac[0][0]:
    characterize_Answer = 1
    character = modelAnsCharac[0][1]
  else:
    characterize_Answer = 0
    character = modelAnsCharac[0][0]

  #imagery
  loaded_model = pickle.load(open('imageryModel.sav', 'rb'))
  vectorizer = pickle.load(open('imageryVectorizer.sav', 'rb'))

  modelAnsImg = loaded_model.predict_proba(vectorizer.transform([line]))
  if modelAnsImg[0][1] > modelAnsImg[0][0]:
    imagery_Answer = 1
    imagery = modelAnsImg[0][1]
  else:
    imagery_Answer = 0
    imagery = modelAnsImg[0][0]

  #juxtaposition
  loaded_model = pickle.load(open('juxtapositionModel.sav', 'rb'))
  vectorizer = pickle.load(open('juxtapositionVectorizer.sav', 'rb'))

  modelAnsJuxt = loaded_model.predict_proba(vectorizer.transform([line]))
  if modelAnsJuxt[0][1] > modelAnsJuxt[0][0]:
    juxtaposition_Answer = 1
    juxtAccuracy = modelAnsJuxt[0][1]
  else:
    juxtaposition_Answer = 0
    juxtAccuracy = modelAnsJuxt[0][0]

  return (metaphor_Answer, characterize_Answer, imagery_Answer,
          0), (metaphorAccuracy, character, imagery, 0)


@app.route('/', methods=['GET', 'POST'])
def index():
  with sqlite3.connect("users.db") as conn:
    curs = conn.cursor()
    curs.execute(
        "CREATE TABLE IF NOT EXISTS previous_texts (username TEXT, previous_text TEXT)"
    )
  method = fk.request.method
  if method == 'POST':
    text = fk.request.form['text']
    if not text:
      return load_input(text, "No text entered")
    else:
      return redirect(url_for('analysis'), 308)

  user = fk.request.cookies.get('login')
  if user:
    user = user.split()
    code = user[1]
    user = user[0]
    with sqlite3.connect("users.db") as conn:
      curs = conn.cursor()
      password = curs.execute(
          "SELECT password FROM user_info WHERE username = ?", [user])
      if (password == code):
        texts = curs.execute(
            "SELECT previous_text FROM previous_texts WHERE username = ?",
            [user])
        texts = texts.fetchall()
        print(texts)
        return load_input(texts=texts)
  return load_input()


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
  with sqlite3.connect("users.db") as conn:
    curs = conn.cursor()
    curs.execute(
        "CREATE TABLE IF NOT EXISTS previous_texts (username TEXT, previous_text TEXT)"
    )
  text = fk.request.form['text']
  user = fk.request.cookies.get('login')
  if user:
    user = user.split()
    code = user[1]
    user = user[0]
    with sqlite3.connect("users.db") as conn:
      curs = conn.cursor()
      password = curs.execute(
          "SELECT password FROM user_info WHERE username = ?", [user])
      if (password == code):
        curs.execute(
            "INSERT INTO previous_texts (username, previous_text) VALUES (?, ?)",
            (user, text))
  textSplit = text.splitlines()
  lines = []
  colors = []
  accuracies = []
  message = ""
  finalMessage = [""]
  for line in textSplit:
    colors = []
    accuracies = []
    color = ""
    message = ""
    print(check_line(line))

    #metaphor
    if check_line(line)[0][0] == 1:
      colors.append('metaphor')
      accuracies.append(check_line(line)[1][0])
      message += """Metaphor -> """ + str(
          round(check_line(line)[1][0] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #characterization
    if check_line(line)[0][1] == 1:
      accuracies.append(check_line(line)[1][1])
      colors.append('characterization')
      message += """Characterization -> """ + str(
          round(check_line(line)[1][1] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #imagery
    if check_line(line)[0][2] == 1:
      colors.append('imagery')
      accuracies.append(check_line(line)[1][2])
      message += """Imagery -> """ + str(round(
          check_line(line)[1][2] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #juxtaposition
    if check_line(line)[0][3] == 1:
      colors.append('juxtaposition')
      accuracies.append(check_line(line)[1][3])
      message += """Juxtaposition -> """ + str(
          round(check_line(line)[1][3] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('noColor')
      accuracies.append(0)
      finalColor = 'noColor'
    print(message)

    finalColor = ""
    minAccuracy = -1
    for i in range(0, len(colors)):
      if colors[i] != "noColor":
        if accuracies[i] > minAccuracy:
          minAccuracy = accuracies[i]
          finalColor = colors[i]
        else:
          continue
    if message == "":
      message = "No literary elements detected."
    messageArr = message.split('\n')
    lineFinal = line.split('\n')
    messageArr[-1] = messageArr[-1].strip()
    print(textSplit)
    lines.append([lineFinal, finalColor, messageArr])
    # import requests

    # url = "https://api.limewire.com/api/image/generation"

    # payload = {
    #     "prompt": """Generate an image that describes the following scene:
    #   A flickering candle beside the clock represents life. It burns brightly for a short while but eventually goes out, leaving only darkness.The scene depicts life as a meaningless play, a performance by a foolish actor who worries and struts for a brief time before disappearing into oblivion.The whole scene is a commentary on the transient nature of life and the emptiness of our pursuits, symbolized by the clock, the shadows, the candle, and the play.""",
    #     "aspect_ratio": "1:1"
    # }

    # headers = {
    #     "Content-Type":
    #     "application/json",
    #     "X-Api-Version":
    #     "v1",
    #     "Accept":
    #     "application/json",
    #     "Authorization":
    #     "Bearer insert API Key HERE"
    # }

    # response = requests.post(url, json=payload, headers=headers)

    # imageLink = response.json()['asset_url']
    imageLink = """https://ai-studio-assets.limewire.media/u/929f5c8f-d590-4a01-bea9-c984a2fa310a/image/0f3cdb1d-e6be-49f9-a808-363b652351a9?Expires=1715621301&Signature=r0OHZIHme8pUe7~2h3VHgASprjytxIyAccpI6KEElHpSkeWBr8OIJ28hnX6-BoXx9ONOCr1~Bne3rzZ1~4iWThSovuwey6RHIxFeMmhrlFJXg0K-cmez2~e0gsVNUZULHepv-WubaKR13qv29BYp2o2P-tptTk-gDqLK0i~e9tL~~XhTEBry9cxiQ2DZYXoYSWN7-tUMVzi8C7Zr27o2Fx4kKpxECVlHMQlJ43yKta7KjQswX7ykt5TdCOJrbOgwIMFI3HE0BIsphIzKDIOYKCs3UVbN3aiqiUI0K4LFOS7x9GEs4jsMiLbDgjqvA9FysqpeRw8HTrr3~~luBQGpSA__&Key-Pair-Id=K1U52DHN9E92VT"""
  return rt("analysis.html", text_in=textSplit, lines=lines)


@app.route('/login', methods=['GET', 'POST'])
def login():
  cookie = fk.request.cookies.get("login")
  if (cookie):
    return redirect("/")
  with sqlite3.connect("users.db") as conn:
    curs = conn.cursor()
    curs.execute(
        "CREATE TABLE IF NOT EXISTS user_info (username TEXT, password TEXT)")
    #the previous text will be the inputed text, so the code will re-analise it, this is easier as we don't have to figure out how to save the analysis.
    m = fk.request.method
    if (m == "POST"):
      t = fk.request.form['tim']
      if (t == "sign"):
        u = escape(fk.request.form['user'])
        p = escape(fk.request.form['pass'])
        c = escape(fk.request.form['con'])
        e = ""
        if (p != c):
          return rt("login.html",
                    error=["Passwords do not match", ""],
                    u=[u, ""],
                    p=["", ""],
                    c="")
        if (u.strip() == ""):
          u = u.strip()
          e = e + "No username entered,"
        if (p.strip() == ""):
          p = p.strip()
          e = e + "No password entered,"
        if (c.strip() == ""):
          c = c.strip()
          e = e + "No password confirmation entered,"
        if (e):
          return rt("login.html", error=[e, ""], u=[u, ""], p=[p, ""], c=c)
        w = curs.execute("SELECT username FROM user_info WHERE username = ?",
                         [u])
        if (w.fetchone()):
          return rt("login.html",
                    error=["Username already taken", ""],
                    u=["", ""],
                    p=[p, ""],
                    c=c)
        #Jake, make sure to sha256 the passwords when it's save, and whatever the extra thing was, just make it secure!
        else:
          secure = makeSecure(p)
          curs.execute(
              "INSERT INTO user_info (username, password) VALUES (?, ?)",
              (u, secure))
          resp = fk.make_response(
              rt("login.html", error=["", ""], u=["", ""], p=["", ""], c=""))
          resp.set_cookie("login", u + " " + makeSecure(p))
          return resp
      elif (t == "log"):
        u = escape(fk.request.form['user1'])
        p = escape(fk.request.form['pass1'])
        w = curs.execute("SELECT password FROM user_info WHERE username = ?",
                         [u])
        passW = w.fetchone()
        if (passW and passW[0] == (makeSecure(p))):
          resp = fk.make_response(
              rt("login.html", error=["", ""], u=["", ""], p=["", ""], c=""))
          resp.set_cookie("login", u + " " + makeSecure(p))
          return resp
        return rt("login.html",
                  error=["", "Username and password do not match"],
                  u=["", u],
                  p=["", ""],
                  c="")
  return rt("login.html", error=["", ""], u=["", ""], p=["", ""], c="")


def makeSecure(p):
  b = "Jake"
  s = bytes(b, 'utf-8')
  return hmac.new(s, str(p).encode("utf-8"), "md5").hexdigest()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)
