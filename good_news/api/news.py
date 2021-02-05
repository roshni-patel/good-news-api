import requests 
from pprint import pprint
import os
import json 
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
import urllib 
from .store import delete_collection, get_articles_collection, set_updated_time

# TODO make multiple requests to get more articles
def get_raw_news():
    NEWS_API_KEY = os.getenv('X_API_KEY')
    headers = {'X-Api-Key': NEWS_API_KEY}
    d = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    params = { 
        'sources': ','.join(["Buzzfeed","Google News", "New York Times", "The Huffington Post", "CNN", "NBC News", "The Washington Post", "ABC News", "BBC News", "Next Big Future", "New Scientist", "Medical News Today", "TechCrunch", "Ars Technica", "Wired", "The Next Web", "Bloomberg", "The Wall Street Journal", "Business Insider"]),
        'language': 'en', 
        'from': d, 
        'pageSize': 100, 
        'sortBy': 'popularity'
    }
    # print(f'https://newsapi.org/v2/everything?{urllib.parse.urlencode(params)}')
    response = requests.get(f'https://newsapi.org/v2/everything?{urllib.parse.urlencode(params)}', headers=headers)
    return response.json() 


# only import for named classes
def update_articles(db):
    good_news = get_good_news()
    articles_collection = get_articles_collection(db) # collection ref.
    # clear existing and store these 
    delete_collection(articles_collection) # clears article collection 
    for article in good_news:
        articles_collection.add(article)
    set_updated_time(db)


def get_good_news():
    raw_news = get_raw_news()
    # print(f'raw news', len(raw_news['articles']))
    good_news = process_news(raw_news) 
    # good_news = json.loads(test_news)
    # print(f'good news', len(good_news))
    return good_news

def process_news(news):
    AZURE_KEY = os.getenv('OCP_APIM_SUBSCRIPTION_KEY')
    headers = {'Ocp-Apim-Subscription-Key': AZURE_KEY, 'Content-Type': 'application/json', 'Accept': 'application/json'}
    request_body = {
        "documents": []
    }

    # pare down news to be a collection with news image in it 
    news['articles'] = [article for article in news['articles'] if article['urlToImage']]
    batch_count = 0 
    for i in range(len(news['articles'])):
        article = news['articles'][i]
        request_body["documents"].append({"language": "en", "id": str(i), "text": article["title"]})
        batch_count += 1 
        # in a batch of 44, triggers after 10, 20, 30, 40, 44
        # in a batch of 43, triggers after 10, 20, 30, 40, 43

        if batch_count == 10:
            response = requests.post('https://good-news-test.cognitiveservices.azure.com/text/analytics/v3.0/sentiment', json = request_body, headers=headers)
            json_data = response.json()
            for result in json_data["documents"]:
                article_pos = int(result["id"])
                news["articles"][article_pos]["sentiment"] = result 
            batch_count = 0 
            request_body = {"documents": []}
    if batch_count > 0: 
        # we had some partial
        response = requests.post('https://good-news-test.cognitiveservices.azure.com/text/analytics/v3.0/sentiment', json = request_body, headers=headers)
        json_data = response.json()
        # print(json_data)
        for result in json_data["documents"]:
            article_pos = int(result["id"])
            news["articles"][article_pos]["sentiment"] = result 
    # print(f'image news', len(news['articles']))
    return filter_news(news) 
    # return news

    # return list(filter(filter_news, news))

# pprint(process_news(json.loads(news))) # testing some data 

# after making the requests for sentiment, we want to filter those results into only those that are neutral/positive 
# array of dictionaries representing articles 
def filter_news(news):
    filtered = []
    for article in news['articles']:
        if article["sentiment"]["sentiment"] == "positive":
            filtered.append(article)
    return filtered 