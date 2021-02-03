from datetime import datetime 

ARTICLES_COLLECTION = 'articles'
USERS_COLLECTION = 'users'
CACHED_COLLECTION = 'configuration'

def delete_collection(coll_ref, batch_size):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

def get_articles_collection(db):
    return db.collection(ARTICLES_COLLECTION)

# get gets the doc, but to get values we have to use todict
def last_updated_time(db):
    return db.collection(CACHED_COLLECTION).document('document_cache').get().to_dict().get('last_updated', datetime.min) # delete key from doc to force reload, oldest possible date

# could initialize class
def set_updated_time(db):
    db.collection(CACHED_COLLECTION).document('document_cache').set({'last_updated': datetime.now()})
