import os

from flask import Flask
from flask_pymongo import PyMongo
from flask_mongo_sessions import MongoDBSessionInterface

from payments.providers.stripe.controller import stripe_bp
from payments.providers.gocardless.controller import gocardless_bp
from payments.providers.paypal.controller import paypal_bp

Flask.secret_key = os.environ['FLASK_SECRET']

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ['MONGO_DATABASE']
mongo = PyMongo(app)
with app.app_context():
    app.session_interface = MongoDBSessionInterface(app, mongo.db, 'sessions')

from payments.controller import *

app.register_blueprint(stripe_bp, url_prefix='/stripe')
app.register_blueprint(gocardless_bp, url_prefix='/gocardless')
app.register_blueprint(paypal_bp, url_prefix='/paypal')