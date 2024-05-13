import pandas as pd
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import string

data = pd.read_csv('metaphorData.csv')
data = data.drop_duplicates()
print("read and drop duplicates")

#The following method is used to clean the text when provided as an input.
def cleanTextFunction(text):
  noPunct = [char for char in text if char not in string.punctuation]
  noPunct = ''.join(noPunct)
  return [word for word in noPunct.split()]

print("clean")

trainX = data.iloc[:, 0].apply(cleanTextFunction)
print(trainX)


transformCount = CountVectorizer(analyzer=cleanTextFunction).fit(data["phrase"])
titleCount = transformCount.transform(data["phrase"])

tfdifTransform = TfidfTransformer().fit(titleCount)
tfdfTitle = tfdifTransform.transform(titleCount)

x = tfdfTitle
y=data.metaphorDetect

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

#Naive Bayes Model
from sklearn.naive_bayes import MultinomialNB
model = MultinomialNB().fit(X_train ,y_train )

#Metrics
all_prediction = model.predict(X_test)
from sklearn.metrics import accuracy_score
print("accuracy:",accuracy_score(y_test, all_prediction))

testing = " this is a good thing"
modelAns = model.predict(transformCount.transform([testing]))[0]

if (modelAns == 1):
  print("This is a metaphor.")
else:
  print("This is not a metaphor.")