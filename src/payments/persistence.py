import os

# we'll need this to store payment results
from pymongo import MongoClient
client = MongoClient(os.environ['MONGO_URI'])
db = client[os.environ['MONGO_DATABASE']]

class LookupException(Exception):
    def __init__(self, message):
        self.message = message
        
    def __repr__(self):
        return self.message

def lookup_ref(ref):
    cursor = db.payments.find({'_id' : ref})
    if cursor.count() == 1:
        return cursor.next()
    else:
        raise LookupException("No record of %s found" % ref)