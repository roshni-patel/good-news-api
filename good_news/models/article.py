class Article: 
    def __init__(self, id=None, title=None, author=None, source_id=None, source_name=None, 
        description=None, image_url=None, article_url=None, publication_date=None, content=None):

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
            'title': self.title, 
            'author': self.author, 
            'source_id': self.source_id,
            'source_name': self.source_name,
            'description': self.description, 
            'image_url': self.image_url, 
            'article_url': self.article_url, 
            'publication_date': self.publication_date, 
            'content': self.content
            }


    def __repr__(self):
        return f'<Article {self.id}' 

    @classmethod 
    def from_firebase(cls, doc):
        doc_dict = doc.to_dict()
        article = cls.from_dict(doc_dict)
        article.id = doc.id 
        return article
    
    @classmethod
    def from_dict(cls, doc_dict):
        return Article(
            title=doc_dict['title'],
            author=doc_dict.get('author'), 
            source_id=doc_dict['source']['id'], 
            source_name=doc_dict['source']['name'], 
            description=doc_dict.get('description'),
            image_url=doc_dict.get('image_url'),
            article_url=doc_dict.get('article_url'),
            publication_date=doc_dict.get('publication_date'),
            content=doc_dict.get('content'))
