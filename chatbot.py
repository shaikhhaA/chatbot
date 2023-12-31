import json
import pickle
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer=WordNetLemmatizer()
import numpy as np
import random
intentsa = json.loads(open('intentsa.json', encoding="utf8" ).read())
wordsa = pickle.load(open('wordsa.pkl','rb'))
classesa = pickle.load(open('classesa.pkl','rb'))
modela = load_model('chatbotmodela.h5')
# -------------- Cleaning the text -------------------
def clean_up_sentencea(sentence):
    # tokenize the pattern - split wordsa into array
    sentence_wordsa = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_wordsa = [lemmatizer.lemmatize(word.lower()) for word in sentence_wordsa]
    return sentence_wordsa
def bow(sentence, wordsa):
    # tokenize the pattern
    sentence_wordsa = clean_up_sentencea(sentence)
    # bag of wordsa - matrix of N wordsa, vocabulary matrix
    bag = [0]*len(wordsa)
    for s in sentence_wordsa:
        for i,w in enumerate(wordsa):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
    return(np.array(bag))
# -----------prediction of wordsa depending on the keras model--------------
def predict_classa(sentence):
    # filter out predictions below a threshold
    p = bow(sentence, wordsa)
    res = modela.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classesa[r[0]], "probability": str(r[1])})
    return return_list
# ------------predict the response-------------
def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents'] #intentsa.json
    for i in list_of_intents:
        if(i['tag']== tag):
            #create a random response fromt he list or responeses
           result = random.choice(i['responses'])
           break
    return result
def chatbot_response(msg):
    ints = predict_classa(msg)
    res = getResponse(ints, intentsa)
    return res

from flask import Flask, render_template, request
import mysql.connector
app = Flask(__name__)

@app.route('/')
def chatbot():
  return render_template("profile.html")
@app.route("/get")
def get_bot_reponse():
  userText = request.args.get('msg')
  return str(chatbot_response(userText))

if __name__ == "__main__":
  app.run(debug=True)
