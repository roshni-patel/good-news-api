class Article: 
    def __init__(self, id=None, title=None, author=None, source_id=None, source_name=None, 
        description=None, image_url=None, article_url=None, publication_date=None, content=None, sentiment=None):

        self.id = id 
        self.title = title
        self.author = author
        self.source_id = source_id 
        self.source_name = source_name 
        self.description = description
        self.image_url = image_url 
        self.article_url = article_url 
        self.publication_date = publication_date 
        self.content = content 
        self.sentiment = sentiment

# we don't have id bc it dsn't belong in body of doc 
# when we create 
    def to_firebase(self):
        return { 
            'title': self.title, 
            'author': self.author, 
            'source': {'id': self.source_id, 'name': self.source_name},
            'description': self.description, 
            'image_url': self.image_url, 
            'article_url': self.article_url, 
            'publication_date': self.publication_date, 
            'content': self.content
            }
    

    def to_json(self): 
        return { 
            'id': self.id,
            'title': self.title, 
            'author': self.author, 
            'source_id': self.source_id,
            'source_name': self.source_name,
            'description': self.description, 
            'image_url': self.image_url, 
            'article_url': self.article_url, 
            'publication_date': self.publication_date, 
            'content': self.content,
            'sentiment': self.sentiment
            }


    def __repr__(self):
        return f'<Article {self.id}' 

    @classmethod 
    def from_firebase(cls, doc):
        doc_dict = doc.to_dict()
        article = cls.from_dict(doc_dict)
        # we use doc directly, to get id, what other attribs are available??
        article.id = doc.id 
        return article

    @classmethod 
    def from_user_article(cls, article_id, article_dict):
        article = cls.from_dict(article_dict)
        article.id = article_id
        return article
    
    # maybe add from json/api, how we create an article 
    @classmethod
    def from_dict(cls, doc_dict):
        return Article(
            title=doc_dict['title'],
            author=doc_dict.get('author'), 
            source_id=doc_dict['source']['id'], 
            source_name=doc_dict['source']['name'], 
            description=doc_dict.get('description'),
            image_url=doc_dict.get('urlToImage'),
            article_url=doc_dict.get('url'),
            publication_date=doc_dict.get('publishedAt'),
            content=doc_dict.get('content'),
            sentiment=doc_dict['sentiment']['sentiment']
        )