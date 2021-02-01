from flask import Flask, jsonify
import json 
from dotenv import load_dotenv
load_dotenv()
import requests 
from flask_cors import CORS


import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin.exceptions import FirebaseError
from good_news.models.user import User 
from good_news.models.article import Article 
from good_news.api.news import get_good_news

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

# write helper to get and set last updated time 
# anytime react asks for current articles, check the last updated time, if i'm still within timeout period, just return existing 
# cached articles, otherwise perform the news request, update the cached, return firebase data 
# could add in an endpoint that does a refresh 


ARTICLES_COLLECTION = 'articles'

@app.route('/articles', methods=('GET',))
def get_articles():
    docs =  db.collection(ARTICLES_COLLECTION).stream()
    articles = [Article.from_firebase(doc) for doc in docs]
    json_articles = [article.to_json() for article in articles]
    return jsonify(json_articles)

@app.route('/api-articles', methods=('GET',))
def get_api_articles():
    good_news = get_good_news()
    return jsonify(good_news)


if __name__ == '__main__':
    app.run(debug=True)