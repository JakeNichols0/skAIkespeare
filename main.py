from flask import redirect, url_for
import flask as fk
from flask import render_template as rt
from html import escape
import pickle
import sqlite3
import hmac

app = fk.Flask(__name__)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=80)


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
      colors.append('lightgreen')
      accuracies.append(check_line(line)[1][0])
      message += """Metaphor -> """ + str(
          round(check_line(line)[1][0] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #characterization
    if check_line(line)[0][1] == 1:
      accuracies.append(check_line(line)[1][1])
      colors.append('lightblue')
      message += """Characterization -> """ + str(
          round(check_line(line)[1][1] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #imagery
    if check_line(line)[0][2] == 1:
      colors.append('lightcoral')
      accuracies.append(check_line(line)[1][2])
      message += """Imagery -> """ + str(round(
          check_line(line)[1][2] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)

    #juxtaposition
    if check_line(line)[0][3] == 1:
      colors.append('purple')
      accuracies.append(check_line(line)[1][3])
      message += """Juxtaposition -> """ + str(
          round(check_line(line)[1][3] * 100, 2)) + """% confidence\n"""
    else:
      colors.append('None')
      accuracies.append(0)
    print(message)

    finalColor = ""
    minAccuracy = -1
    for i in range(0, len(colors)):
      if colors[i] != "None":
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
    imageLink = """https://ai-studio-assets.limewire.media/u/929f5c8f-d590-4a01-bea9-c984a2fa310a/image/4b36e33c-df47-47f7-b469-4e2d7b369e31?Expires=1715535725&Signature=v-koYYhLMqo0maVHXZpCQkKU2agvOrQO4u2giC~OaYA8BlnLZsMAsZWqX4JiKnIRcfMqYIfl3iEnIrq67FGDtl8fpQmxDXBJaybOF4Cwi3Lb2aHzfS5zwOEqoecCEXrlqybuyEIvKnZeNQvzaBQhFLvpo9qQcQFW0yGOwxDS9uB9-7rMtyyj0unDQfbWt2985jt~SrcMmN5Jrx79MUch7FKr8ba7y5Lt9zotXV80BfLzZCVMfBcBP7Lz1r5JwKhlc-TuSxaQnU~nD0hLWs0Qq8G6Td11YSuVzuI3lmEx9W2IPQV1bDNj7q9YybCqjyMd6mpmQQ8ci1pTGEh1GwS-WA__&Key-Pair-Id=K1U52DHN9E92VT"""
  return rt("analysis.html", text_in=textSplit, lines=lines, link=imageLink)


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
