import os, pymongo

client = pymongo.MongoClient(os.environ['MONGO_URI'])
db = client.get_default_database()
payments_db = db['payments']


class LookupException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return self.message

def lookup_ref(ref):
    cursor = payments_db.find({'_id' : ref})
    if cursor.count() == 1:
        return cursor.next()
    else:
        raise LookupException("No record of %s found" % ref)