from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pprint
import datetime as dt
from mongoengine import *
import numpy as np
import pandas as pd
from pandas import *
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db"
mongo = PyMongo(app)

#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scrape")
def scrape_all():
    results = mongo.mars_db.mars
    # db = client.mars_db
    # mars = db.mars
    # for item in mars.find().limit(10000):
        
    #     pprint(item)
    scrape = scrape_mars.scrape()
    # results.update({}, mars_data, upsert=True)
    
    # db.mars.find()  <-- shows all the items in the mars collection
    # listings = mongo.db.listings
    # listings_data = scrape_craigslist.scrape()
    # listings.update({}, listings_data, upsert=True)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
