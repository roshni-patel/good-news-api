from flask import Flask, jsonify, request
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
from good_news.api.news import get_good_news, update_articles
from good_news.api.store import (ARTICLES_COLLECTION, USERS_COLLECTION, CACHED_COLLECTION, 
    last_updated_time)
import os


from datetime import datetime, timedelta

cred = credentials.Certificate({
    "type": os.getenv('FIREBASE_TYPE'),
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace("\\n", "\n"),
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT')
}) 
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)

# write helper to get and set last updated time 
# anytime react asks for current articles, check the last updated time, if i'm still within timeout period, just return existing 
# cached articles, otherwise perform the news request, update the cached, return firebase data 
# could add in an endpoint that does a refresh 
def is_update_required():
    last_time = last_updated_time(db)
    max_diff = timedelta(days=1)
    now = datetime.now(tz=last_time.tzinfo) 
    difference = now - last_time

    return difference > max_diff 


@app.route('/', methods=('GET',))
def get_articles():
    if is_update_required(): 
        update_articles(db)

    # regardless, we still want to retrieve whatever's stored in articles
    
    # when we use stream it gives us the doc directly 
    docs =  db.collection(ARTICLES_COLLECTION).stream()
    articles = [Article.from_firebase(doc) for doc in docs]
    json_articles = [article.to_json() for article in articles]
    return jsonify(json_articles)


@app.route('/users/<id>/articles', methods=('GET',))
def get_saved_articles(id):
    # user document 
    # error checking for if user cant be found 
    doc = db.collection(USERS_COLLECTION).document(id).get() 
    user = User.from_firebase(doc)
    user_articles = user.saved_articles
    json_articles = [article.to_json() for article in user_articles] # added back in 
    return jsonify(json_articles) # lets flask know about headers to send in respose
    # we want to generate json that represents an article
    # i need a collection of articles, then I can call to json to
    # if user saved articles is a list of ids, i need to iterate and retrieve each article 


@app.route('/users/<uid>/articles/<aid>', methods=('POST', 'DELETE')) 
def save_unsave_article(uid, aid):
    # could be a bad user or article
    user_doc_ref = db.collection(USERS_COLLECTION).document(uid)
    article_doc_ref = db.collection(ARTICLES_COLLECTION).document(aid)
    if request.method == 'POST':
        try:
            user_doc_ref.update({f'saved_articles.{aid}': article_doc_ref.get().to_dict()})
            return jsonify({'Success': 'This article has been added to your saved articles'}) # could put ok true, false 
        except FirebaseError:
            return jsonify({'Error': 'There was an issue with saving that article'})
    else:
        try:
            user_doc_ref.update({f'saved_articles.{aid}': firestore.DELETE_FIELD})
            return jsonify({'Success': 'This article has been removed from your saved articles'}) 
        except FirebaseError:
            return jsonify({'Error': 'There was an issue with unsaving that article'}) 


if __name__ == '__main__':
    app.run(debug=True)