from flask import Flask, jsonify, request, redirect, url_for, render_template
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from splinter import Browser
import pprint
import datetime as dt
# from mongoengine import *
import numpy as np
import pandas as pd
from pandas import *
from scrape_mars import *
import os

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_db" 
mongo = PyMongo(app)


#################################################
# Flask Routes
#################################################

@app.route("/")
def index():
    # fetch our data object (dictionary) from MongoDB here
    print('Fetching mars data from mongo...')
    mars_data = mongo.db.mars_collection.find_one()

    print(mars_data)

    return render_template("index.html", results=mars_data)

@app.route("/scrape")
def scrape_all():
    # perform scrape function -> and capture the results (final dictionary)
    mars_data = scrape() # outputs {mars data...}

    # connect to mongodb
    mars_collection = mongo.db.mars_collection

    # insert into mongodb, replacing old data if there is any
    mars_collection.update({}, mars_data, upsert=True)
    
    # use this to test mars_data dictionary collection displays in html 
    # return jsonify(mars_data) 
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)
