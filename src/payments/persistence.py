# we'll need this to store payment results
from payments.config import mongo_host, mongo_port
from pymongo import MongoClient
client = MongoClient(mongo_host, mongo_port)