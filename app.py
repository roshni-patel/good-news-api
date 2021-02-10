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


from datetime import datetime, timedelta


cred = credentials.Certificate("serviceAccountKey.json") # NOTE - for deployment where does this need to be kept? currently in gitignore 
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

# maybe should change this to be just / so articles is the homepage? 
@app.route('/articles', methods=('GET',))
def get_articles():
    if is_update_required(): 
        update_articles(db)

    # regardless, we still want to retrieve whatever's stored in articles
    
    # when we use stream it gives us the doc directly 
    docs =  db.collection(ARTICLES_COLLECTION).stream()
    articles = [Article.from_firebase(doc) for doc in docs]
    json_articles = [article.to_json() for article in articles]
    return jsonify(json_articles)

# @app.route('/api-articles', methods=('GET',))
# def get_api_articles():
#     good_news = get_good_news()
#     return jsonify(good_news)

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

# just send user id
# grab existing user document from users collection matching id given, check to see if they already have columns
# if not update that user document to have full set of data items 
# add to user provider 
# when a user logs in, backend make sure to migrate this user, read the existing values and try and move them into expected fields defined 
# just send the user id, grab the existing user doc from users collection, and check if they already have the columns expected for full user, if not update
# to have full set of data items 
# async user provider 

# how google user stored in firestore - displayName, email, photoURL
# @app.route('/users/<uid>', methods=('POST',))
# def migrate_user(uid):
#     user_doc_ref = db.collection(USERS_COLLECTION).document(uid)

#     FIELDS = ['name', 'email', 'saved_articles', 'filtered_articles', 'time_preference']
#     # for field in FIELDS: 
#     #     if user_doc_ref.get().to_dict().get(field) is None: 
#     #         user_doc_ref.get().update

#     name = user_doc_ref.get().to_dict()['displayName'] 
#     email = user_doc_ref.get().to_dict()['email']
#     saved_articles = user_doc_ref.get().update()

# # we are returning json that represents the User instance?
#     return jsonify()




if __name__ == '__main__':
    app.run(debug=True)