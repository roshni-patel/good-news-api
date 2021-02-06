from .article import Article

class User: 
    def __init__(self, id=None, name=None, email=None, saved_articles=None, filtered_articles=None, time_preference=None): # evaluated only once
        self.id = id 
        self.name = name 
        self.email = email 
        self.saved_articles = saved_articles or [] # can't iterate over none
        self.filtered_articles = filtered_articles or []
        self.time_preference = time_preference

    def to_firebase(self):
        return { 
            'name': self.name, 'email': self.email, 'saved_articles': self.saved_articles, 
            'filtered_articles': self.filtered_articles, 'time_preference': self.time_preference 
        }
    
    def __repr__(self):
        return f'<User {self.id}'

# firebase.collection.user to iterate, turn generic firebase structure into strongly typed user 
    @classmethod 
    def from_firebase(cls, doc):
        doc_dict = doc.to_dict()
        user = cls.from_dict(doc_dict)
        user.id = doc.id 
        return user 
    
    # we did this with article, because we;re getting from api articles and initialize from firebase dict 
    # for users we don't have api, we own this type, one source for serialized format, whatever user is stored
    # as in firebase 
    @classmethod
    def from_dict(cls, doc_dict):
        saved_articles = [Article.from_user_article(article_id, article_content) for article_id, article_content in doc_dict['saved_articles'].items()]

        return User(
            name=doc_dict['name'],
            email=doc_dict['email'],
            saved_articles=saved_articles, 
            filtered_articles=doc_dict['filtered_articles'],
            time_preference=doc_dict['time_preference']
        )
    

    def to_json(self): 
        return { 
            'name': self.name, 
            'email': self.email, 
            'saved_articles': self.saved_articles,
            'filtered_articles': self.filtered_articles,
            'time_preference': self.time_preference
        }




