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
    # json_articles = [article.to_json() for article in user_articles]
    return jsonify(user_articles) # lets flask know about headers to send in respose
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
            return jsonify({'Success': 'This article has been added to your saved articles'}) 
        except FirebaseError:
            return jsonify({'Error': 'There was an issue with saving that article'})
    else:
        try:
            user_doc_ref.update({f'saved_articles.{aid}': firestore.DELETE_FIELD})
            return jsonify({'Success': 'This article has been removed from your saved articles'}) 
        except FirebaseError:
            return jsonify({'Error': 'There was an issue with unsaving that article'}) 


# @app.route('/users/<id>', methods=('GET', 'POST'))
# def show_edit_profile(id):
#     if request.method == 'POST':
#         doc_ref = db.collection(USERS_COLLECTION).document(id) # is doc ref just grabbing the specific doc? 
#         user = User.from_firebase(doc_ref.get())
#         user.time_preference = request.form['time_preference']

#         try: 
#             doc_ref.update(user.to_firebase())
#             return jsonify({'Success': 'Your profile has been updated'})  
#         except FirebaseError:
#             return jsonify({'Error': 'There was an issue updating your profile'})  
#     else:
#         doc_ref = db.collection(USERS_COLLECTION).document(id)
#         user = User.from_firebase(doc_ref.get())
#         return jsonify(user)


# @app.route('users/<id>/filtered', methods=('GET',)):
# def get_filtered_articles(id):
#     doc_ref = db.collection(USERS_COLLECTION).document(id)



# @app.route('/users/<uid>/filtered/<aid>', methods=('POST', 'PATCH')):
# def filter_or_unfilter_article(uid, aid):
#     user_doc_ref = db.collection(USERS_COLLECTION).document(uid)
#     article_doc_ref = db.collection(ARTICLES_COLLECTION).document(aid)

#     # need to push filtered out article into the array for the specific user 
#     # filtered = request.form['aid']
#     if request.method == 'POST':
#         try: 
#             user_doc_ref.update({'filtered_articles': firestore.ArrayUnion(['aid'])})
#             user_doc_ref.update({'filtered_articles': firestore.ArrayUnion([article_doc_ref.get()])})
#             return jsonify({'Success': 'This article has been removed from your feed'})
#         except FirebaseError: 
#             return jsonify({'Error': 'There was an issue with removing this article from your feed'})
#     else: 
#         try: 
#             user_doc_ref.update({'filtered_articles': firestore.ArrayRemove(['aid'])})
#             user_doc_ref.update({'filtered_articles': firestore.ArrayRemove([article_doc_ref.get()])})
#             return jsonify({'Success': 'This article has been added back to your feed.'})
#         except FirebaseError: 
#             return jsonify({'Error': 'There was an issue with adding this article back to your feed'})

if __name__ == '__main__':
    app.run(debug=True)