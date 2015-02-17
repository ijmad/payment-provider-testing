from flask import Flask
from flask_pymongo import PyMongo
from flask_mongo_sessions import MongoDBSessionInterface

Flask.secret_key = '12345'

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'payments'
mongo = PyMongo(app)
with app.app_context():
    app.session_interface = MongoDBSessionInterface(app, mongo.db, 'sessions')

from payments.controller import *
